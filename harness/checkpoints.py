import pwn
import math


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("binary", nargs=1)
    args = parser.parse_args()
    binary_path = args.binary
    crashed = False
    io = pwn.process(['gdb', binary_path[0]])
    io.sendline(b'break main')
    io.sendline(b'break _fini')
    io.sendline(b'r')
    io.sendline(b'checkpoint')
    io.recvuntil(b'checkpoint ', drop=True)
    index = io.recvuntil(b':', drop=True)
    io.sendline(b'continue')
    io.kill()
    header = None
    chk_pt_index = 1
    with open('./binaries/csv1.txt', 'rb') as f:
        header = f.readline()
    print(header)
    pld_iter = gen_payload_csv(header)
    while (not crashed):
        io = pwn.process(binary_path)
        payload = next(pld_iter)
        io.sendline(payload)
        io.wait()
        # if len(bytes_fini) == 0:
        #     print(bytes_fini)
        #     print('hangs')


def gen_payload_csv(header):
    n_cols = len(header.decode().split(','))
    seed = 0
    while True:
        if seed == 0:
            yield header + seed.to_bytes(4, 'big')
        else:
            cell_len = math.floor(math.log(seed, 0xff))
            if cell_len == 0:
                cell_len = 1
            bytes = seed.to_bytes(cell_len * 4, 'big')
            payload = [bytes[i:i + cell_len] for i in range(n_cols)]
            payload = b','.join(payload)
            yield header + payload
        seed += 1


if __name__ == '__main__':
    main()
