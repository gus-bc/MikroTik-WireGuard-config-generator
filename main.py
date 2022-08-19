import os
import json
import subprocess
import ipaddress


def load_data(file_name):
    with open(file_name) as unloaded_data:
        loaded_data = json.load(unloaded_data)
        return loaded_data


def main():
    config_file = input("Name of config file: ")
    data = load_data(config_file)
    int_start_ip = int(ipaddress.IPv4Address(data['config']["start_ip"]))
    int_end_ip = int(ipaddress.IPv4Address(data['config']["end_ip"]))
    dns = data['config']['DNS']
    peer = data['config']['peer']

    os.system(f"mkdir WireGuard_{config_file}_files")
    os.chdir(f"WireGuard_{config_file}_files")
    firewall_add = ""
    for i in range(int_end_ip-int_start_ip+1):
        str_ip = str(ipaddress.IPv4Address(int_start_ip + i))
        priv_key = subprocess.run(['wg', 'genkey'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        print("priv_key: ", priv_key)
        pub_key = subprocess.run(['wg', 'pubkey'], stdout=subprocess.PIPE, input=priv_key, text=True).stdout
        print("pub_key: ", pub_key)

        conf_file = f"[Interface]\n" \
                    f"PrivateKey = {priv_key}" \
                    f"Address = {str_ip}\n" \
                    f"DNS = {dns}" \
                    f"\n\n[Peer]\n" + peer
        if data['config']["preshared-key"]:
            conf_file += f"\nPresharedKey={data['config']['preshared-key']}"

        os.system(f'echo "{conf_file}" > {str_ip}.conf')
        firewall_add += 'add allowed-address={}/32 interface={} public-key="{}" \n'.format(str_ip, data['config']["interface"], pub_key[:-1])
        if data['config']["preshared-key"]:
            firewall_add = firewall_add[:-1] + 'preshared-key="{}"\n'.format(data['config']["preshared-key"])


    print(firewall_add)
    os.system('touch Firewall_command.txt')
    with open("Firewall_command.txt", "w") as firewall:
        firewall.write(firewall_add)


if __name__ == "__main__":
    main()
