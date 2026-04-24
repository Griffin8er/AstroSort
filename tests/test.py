from AstroSort import fov_checker


results = fov_checker(["M 65", "NGC 3627", "NGC 3628"], padding_percentage=10, fov_width=2.59, fov_height=2.59)

print(results)