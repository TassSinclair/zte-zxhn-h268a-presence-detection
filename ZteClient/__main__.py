from ZteClient import ZteClient

def main():
    zte_client = ZteClient("10.0.0.1", 80, "admin", "password")
    zte_client.login()

if __name__ == '__main__':
    main()