# import math
import random

from src.settings import zkp_settings


class PublicVariableGenerator:
    def get_bits(self) -> int:
        return zkp_settings.bits

    # k selected as per page 188 of Cryptography: An Introduction (3rd Edition) by Nigel Smart.
    def _is_prime(self, n: int, k: int = 20) -> bool:
        if n <= 1:
            return False
        if n <= 3:
            return True

        # Write n as 2^r * d + 1
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2

        # Miller-Rabin primality test
        #   used to test if something is prime with high confidence
        #   pg. 188 in Cryptography: An Introduction
        for _ in range(k):
            a = random.randint(2, n - 2)
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue

            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False

        return True

    def _get_prime(self, bits: int) -> int:
        while True:
            candidate = random.getrandbits(bits)
            if candidate % 2 == 0:
                candidate += 1
            if self._is_prime(candidate):
                return candidate

    def _get_safe_prime(self, bits: int) -> tuple[int, int]:
        while True:
            q = self._get_prime(bits - 1)  # Get a prime of bits-1 to ensure p has 'bits' bits
            p = 2 * q + 1
            if self._is_prime(p):
                return p, q

    def _find_generator(self, p: int, q: int) -> int:
        while True:
            candidate = random.randint(2, p - 2)
            if pow(candidate, 2, p) != 1 and pow(candidate, q, p) == 1:
                return candidate

    # This approach was formulated primarily on Cryptography: An Introduction (3rd Edition) by Nigel Smart.
    class Approach1:
        def __init__(self, generator: "PublicVariableGenerator") -> None:
            self.generator = generator
            self.p, self.q = self.generator._get_safe_prime(self.generator.get_bits())

        def get_public_variables(self) -> tuple[int, int, int, int]:
            p = self.p
            q = self.q
            g = self.generator._find_generator(p, q)
            h = g
            while True:
                h = self.generator._find_generator(p, q)
                if h != g:
                    break

            return p, q, g, h

    # Whilst grappling with this challenge I came across another approach which I my curiosity wanted to investigate.
    # There seems to be some bugs in here, although if you run it enough times it sometimes works :facepalm:
    """
    class Approach2:
        def __init__(self, generator: "PublicVariableGenerator") -> None:
            self.generator = generator
            _, self.q = self.generator._get_safe_prime(self.generator.get_bits())
            self.g = self.generator._find_generator(p, q)

        # Euler's totient
        #   also known as Euler's totient
        #   used to test for primitive roots
        #   pg. 5 in Cryptography: An Introduction
        #   Can be used to verify if a candidate is a generator by checking if pow(candidate, phi(q), q) == 1, where phi(q) is q-1
        def _eulers_phi_function(self, n: int) -> int:
            result = n
            for p in range(2, int(math.sqrt(n)) + 1):
                if n % p == 0:
                    while n % p == 0:
                        n //= p
                    result -= result // n
            if n > 1:
                result -= result // n
            return result

        def get_verification(self) -> str:
            q = self.q

            a = random.randint(1, 10)
            b = random.randint(1, 10)

            A = pow(self.g, a, q)
            B = pow(self.g, b, q)
            C = pow(self.g, (a * b), q)

            x = 123

            y1 = pow(self.g, x, q)
            y2 = pow(B, x, q)

            k = random.randint(1, self.q - 1)

            s = (x + a * k) % q

            r1_original = pow(self.g, s, q)
            r2_original = pow(B, s, q)

            r1_new = pow(A, s) * y1 % q
            r2_new = pow(C, s) * y2 % q

            if r1_new == r1_original and r2_new == r2_original:
                result = "successfully been authenticated"
            else:
                result = "The ZKP authentication was Unsuccessful"

            return result
        """


if __name__ == "__main__":
    generator = PublicVariableGenerator()

    approach_1 = generator.Approach1(generator)
    p, q, g, h = approach_1.get_public_variables()
    print(f"Approach 1: {p=}, {q=}, {g=}, {h=}\n")

    # approach_2 = generator.Approach2(generator)
    # result = approach_2.get_verification()
    # print(f"Approach 2: {result=}")
