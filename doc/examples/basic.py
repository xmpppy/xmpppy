import sys
import xmpp


def send_message(jabber_id, password, receiver, message):
    jid = xmpp.protocol.JID(jabber_id)
    connection = xmpp.Client(jid.getDomain(), debug=['always'])
    connection.connect()
    connection.auth(jid.getNode(), password, resource=jid.getResource())
    connection.send(xmpp.protocol.Message(receiver, message))


if __name__ == '__main__':
    try:
        sender, password, receiver, message = sys.argv[1:5]
    except:
        raise ValueError('Insufficient arguments. Please supply sender, password, receiver, message.')

    print('INFO: Sending message from {sender} to {receiver}.'.format(**locals()))
    send_message(sender, password, receiver, message)
