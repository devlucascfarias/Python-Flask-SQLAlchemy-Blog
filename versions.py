import pkg_resources

libraries = [
    ""
]

for library in libraries:
    version = pkg_resources.get_distribution(library).version
    print(f"{library}: {version}")
