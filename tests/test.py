from AstroSort import required_fov

result = required_fov.required_fov_from_names(
    ["NGC 3031", "NGC 3034"],
    setup_X=2.59,
    setup_Y=2.59,
    padding_percentage=5
)

print(result)