"""SCRAM mechanism classes for SASL authentication (RFC 5802 / RFC 7677)."""
import os
import base64
import hmac
from hashlib import sha1, sha256, pbkdf2_hmac
from six import ensure_binary, ensure_str
from .protocol import Node, NS_SASL

CHARSET_ENCODING = 'utf-8'


class ScramBase:
    """Base class for SCRAM-SHA-* mechanisms.

    Subclasses set HASH_NAME and HASH_MOD for the specific hash algorithm.
    """
    HASH_NAME = 'sha1'
    HASH_MOD = sha1

    def __init__(self, sasl_owner):
        self.sasl = sasl_owner

    def build_client_first(self, mechanism, cb_type=None, cb_data=b'', cb_available=False):
        """Build initial SCRAM client-first message and initialise state."""
        nonce = base64.b64encode(os.urandom(18)).decode('ascii')
        uses_plus = mechanism.endswith('PLUS')
        gs2_header = self.sasl._scram_build_gs2(
            cb_type if uses_plus else None,
            cb_available=cb_available and not uses_plus,
        )
        client_first_bare = 'n=%s,r=%s' % (self.sasl._scram_escape(self.sasl.username), nonce)
        client_first_message = gs2_header + client_first_bare
        self.sasl.scram_state = {
            'gs2': gs2_header,
            'nonce': nonce,
            'client_first_bare': client_first_bare,
            'server_first': None,
            'cb_data': cb_data if uses_plus else b'',
        }
        payload = base64.b64encode(client_first_message.encode(CHARSET_ENCODING)).decode('ascii')
        return Node('auth', attrs={'xmlns': NS_SASL, 'mechanism': mechanism}, payload=[payload])

    def handle_server_first(self, mechanism, challenge):
        """Handle server-first message and respond with client proof.

        Returns True on success (response sent) or False on failure.
        """
        data = ensure_str(base64.b64decode(challenge.getData()), CHARSET_ENCODING)
        attrs = self.sasl._scram_parse(data)
        if 'e' in attrs:
            self.sasl.startsasl = 'failure'
            self.sasl.DEBUG('SCRAM error: %s' % attrs.get('e'), 'error')
            return False
        state = self.sasl.scram_state
        if state.get('server_first') is not None:
            self.sasl.DEBUG('Unexpected SCRAM challenge state', 'warn')
            return False
        combined_nonce = attrs.get('r', '')
        if not combined_nonce.startswith(state['nonce']):
            self.sasl.startsasl = 'failure'
            self.sasl.DEBUG('SCRAM nonce mismatch', 'error')
            return False
        if len(combined_nonce) <= len(state['nonce']):
            self.sasl.startsasl = 'failure'
            self.sasl.DEBUG('SCRAM server nonce too short', 'error')
            return False
        salt = base64.b64decode(attrs.get('s', ''))
        iterations = int(attrs.get('i', '0'))
        if iterations <= 0:
            self.sasl.startsasl = 'failure'
            self.sasl.DEBUG('SCRAM invalid iteration count', 'error')
            return False
        gs2header = state['gs2']
        cb_data = state.get('cb_data', b'')
        cbind = base64.b64encode(gs2header.encode(CHARSET_ENCODING) + cb_data).decode('ascii')
        salted = pbkdf2_hmac(self.HASH_NAME,
                             ensure_binary(self.sasl.password, CHARSET_ENCODING),
                             salt, iterations)
        client_key = hmac.new(salted, b'Client Key', self.HASH_MOD).digest()
        stored_key = self.HASH_MOD(client_key).digest()
        client_final_no_proof = 'c=%s,r=%s' % (cbind, combined_nonce)
        auth_message = ','.join([state['client_first_bare'], data, client_final_no_proof])
        client_signature = hmac.new(stored_key,
                                    ensure_binary(auth_message, CHARSET_ENCODING),
                                    self.HASH_MOD).digest()
        proof = bytes(a ^ b for a, b in zip(bytearray(client_key), bytearray(client_signature)))
        server_key = hmac.new(salted, b'Server Key', self.HASH_MOD).digest()
        server_signature = hmac.new(server_key,
                                    ensure_binary(auth_message, CHARSET_ENCODING),
                                    self.HASH_MOD).digest()
        state['server_signature'] = base64.b64encode(server_signature).decode('ascii')
        state['server_first'] = data
        resp = '%s,p=%s' % (client_final_no_proof, base64.b64encode(proof).decode('ascii'))
        payload = base64.b64encode(resp.encode(CHARSET_ENCODING)).decode('ascii')
        node = Node('response', attrs={'xmlns': NS_SASL}, payload=[payload])
        self.sasl._owner.send(node.__str__())
        return True


class ScramSHA1(ScramBase):
    HASH_NAME = 'sha1'
    HASH_MOD = sha1


class ScramSHA256(ScramBase):
    HASH_NAME = 'sha256'
    HASH_MOD = sha256


SCRAM_MECHANISMS = {
    'SCRAM-SHA-1':       ScramSHA1,
    'SCRAM-SHA-1-PLUS':  ScramSHA1,
    'SCRAM-SHA-256':     ScramSHA256,
    'SCRAM-SHA-256-PLUS': ScramSHA256,
}
