"""SCRAM mechanism classes for SASL authentication.

Provides a small abstraction over SCRAM mechanisms so the SASL class can
register and use mechanism implementations instead of hardcoding logic.
"""
from hashlib import sha1, sha256
import base64, hmac
from hashlib import pbkdf2_hmac
from six import ensure_binary, ensure_str

CHARSET_ENCODING='utf-8'

class ScramBase:
    """Base class for SCRAM mechanisms.

    Subclasses should set HASH_NAME and HASH_MOD appropriately.
    """
    HASH_NAME = 'sha1'
    HASH_MOD = sha1

    def __init__(self, sasl_owner):
        self.sasl = sasl_owner

    def _b64(self, data):
        # data is bytes
        return base64.b64encode(data).decode('ascii')

    def _b64decode(self, data):
        return base64.b64decode(data)

    def _b64str(self, s):
        # encode a string to base64-as-ascii
        return base64.b64encode(s.encode(CHARSET_ENCODING)).decode('ascii')

    def build_client_first(self, mechanism, cb_type=None, cb_data=b''):
        """Build initial SCRAM client-first message and initialize state.

        Mirrors previous implementation in auth.SASL._build_scram_auth but
        keeps mechanism-specific hash algorithm in the class.
        """
        # Ensure fresh state
        self.sasl.scram_state = {}
        nonce_bytes = __import__('os').urandom(18)
        nonce = base64.b64encode(nonce_bytes).decode('ascii')
        gs2_header = self.sasl._scram_build_gs2(cb_type if mechanism.endswith('PLUS') else None)
        client_first_bare = 'n=%s,r=%s' % (self.sasl._scram_escape(self.sasl.username), nonce)
        client_first_message = gs2_header + client_first_bare
        self.sasl.scram_state = {
            'gs2': gs2_header,
            'nonce': nonce,
            'client_first_bare': client_first_bare,
            'server_first': None,
            'cb_data': cb_data if mechanism.endswith('PLUS') else b'',
        }
        # Build Node locally to avoid depending on SASL methods
        from .protocol import Node, NS_SASL
        return Node('auth', attrs={'xmlns': NS_SASL, 'mechanism': mechanism}, payload=[self._b64str(client_first_message)])

    def handle_server_first(self, mechanism, challenge):
        """Handle server-first message and respond with client proof.

        Returns True on success (sent response) or False on failure (sets startsasl to 'failure').
        """
        data = ensure_str(base64.b64decode(challenge.getData()), CHARSET_ENCODING)
        attrs = self.sasl._scram_parse(data)
        if 'e' in attrs:
            self.sasl.startsasl = 'failure'
            self.sasl.DEBUG('SCRAM error: %s' % attrs.get('e'), 'error')
            return False
        state = self.sasl.scram_state
        if state.get('server_first') is None:
            combined_nonce = attrs.get('r', '')
            if not combined_nonce.startswith(state['nonce']):
                self.sasl.startsasl = 'failure'
                self.sasl.DEBUG('SCRAM nonce mismatch', 'error')
                return False
            if len(combined_nonce) <= len(state['nonce']):
                self.sasl.startsasl = 'failure'
                self.sasl.DEBUG('SCRAM server nonce not long enough', 'error')
                return False
            salt = self._b64decode(attrs.get('s', ''))
            iterations = int(attrs.get('i', '0'))
            if iterations <= 0:
                self.sasl.startsasl = 'failure'
                self.sasl.DEBUG('SCRAM invalid iteration count', 'error')
                return False
            gs2header = state['gs2']
            cb_data = state.get('cb_data', b'')
            cbind = self._b64(gs2header.encode(CHARSET_ENCODING) + cb_data)
            salted = pbkdf2_hmac(self.HASH_NAME, ensure_binary(self.sasl.password, CHARSET_ENCODING), salt, iterations)
            client_key = hmac.new(salted, b"Client Key", self.HASH_MOD).digest()
            stored_key = self.HASH_MOD(client_key).digest()
            client_final_no_proof = 'c=%s,r=%s' % (cbind, combined_nonce)
            auth_message = ','.join([state['client_first_bare'], data, client_final_no_proof])
            client_signature = hmac.new(stored_key, ensure_binary(auth_message, CHARSET_ENCODING), self.HASH_MOD).digest()
            proof_bytes = bytearray(a ^ b for a, b in zip(bytearray(client_key), bytearray(client_signature)))
            proof = bytes(proof_bytes)
            server_key = hmac.new(salted, b"Server Key", self.HASH_MOD).digest()
            server_signature = hmac.new(server_key, ensure_binary(auth_message, CHARSET_ENCODING), self.HASH_MOD).digest()
            state['server_signature'] = base64.b64encode(server_signature).decode('ascii')
            state['server_first'] = data
            resp = '%s,p=%s' % (client_final_no_proof, base64.b64encode(proof).decode('ascii'))
            from .protocol import Node, NS_SASL
            node = Node('response', attrs={'xmlns': NS_SASL}, payload=[self._b64str(resp)])
            self.sasl._owner.send(node.__str__())
            return True
        self.sasl.DEBUG('Unexpected SCRAM challenge state', 'warn')
        return False


class ScramSHA1(ScramBase):
    HASH_NAME = 'sha1'
    HASH_MOD = sha1

class ScramSHA256(ScramBase):
    HASH_NAME = 'sha256'
    HASH_MOD = sha256


# Registry mapping mechanism names to mechanism classes
SCRAM_MECHANISMS = {
    'SCRAM-SHA-1': ScramSHA1,
    'SCRAM-SHA-1-PLUS': ScramSHA1,
    'SCRAM-SHA-256': ScramSHA256,
    'SCRAM-SHA-256-PLUS': ScramSHA256,
}
