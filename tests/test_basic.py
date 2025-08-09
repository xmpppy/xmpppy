def test_cli_send_simple(run, timestamp_iso):
    """
    A basic test case invoking `xmpp-message`.
    """

    # Run command and capture output.
    message = f"Message from CI. Date/Time: {timestamp_iso}"
    result = run(f"xmpp-message --jabberid=testdrive@localhost --password=secret "
                 f"--receiver=testdrive@localhost --message='{message}' --debug")

    # Verify output.
    assert 'Registering namespace "http://etherx.jabber.org/streams"' in result.err
    assert "TLS supported by remote server. Requesting TLS start." in result.err
    assert "Got jabber:client/iq stanza" in result.err
    assert "Expected stanza arrived!" in result.err
    assert "Successfully opened session." in result.err
