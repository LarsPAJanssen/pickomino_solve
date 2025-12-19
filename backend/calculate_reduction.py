import math


def nCr(n, r):
    f = math.factorial
    return f(n) // f(r) // f(n - r)


print(
    f"{'Dice':<5} | {'Permutations':<15} | {'Combinations':<15} | {'Reduction Factor':<15}"
)
print("-" * 60)

total_perms = 0
total_combs = 0

for dice_count in range(1, 9):
    # Permutations: 6^n
    perms = 6**dice_count

    # Combinations with replacement: (n+k-1) choose k, where k=dice_count, n=6 faces
    # Formula is C(n+k-1, k)
    faces = 6
    combs = nCr(faces + dice_count - 1, dice_count)

    ratio = perms / combs
    print(f"{dice_count:<5} | {perms:<15} | {combs:<15} | {ratio:<15.2f}")

    total_perms += perms
    total_combs += combs

print("-" * 60)
print(
    f"Total | {total_perms:<15} | {total_combs:<15} | {total_perms/total_combs:<15.2f}"
)
