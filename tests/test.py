from AstroSort import fov_checker
import time


start = time.time()

result = fov_checker(
    ["NGC 3031", "NGC 3034"],
    fov_width=2.59,
    fov_height=2.59,
    padding_percentage=5
)

middle = time.time()

print(result)
print(f"First call duration: {middle - start:.4f} seconds")

result = fov_checker(
    ["NGC 3623", "NGC 3627", "NGC 3628"],
    fov_width=2.59,
    fov_height=2.59,
    padding_percentage=5
)

end = time.time()

print(result)
print(f"Second call duration: {end - middle:.4f} seconds")