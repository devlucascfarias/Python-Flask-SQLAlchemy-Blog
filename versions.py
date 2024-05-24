import pkg_resources

libraries = [
    "flask",
    "authlib",
    "flask_sqlalchemy",
    "sqlalchemy",
    "python-dotenv"
]

for library in libraries:
    version = pkg_resources.get_distribution(library).version
    print(f"{library}: {version}")

# Output:

# flask: 3.0.2
# authlib: 1.3.0
# flask_sqlalchemy: 3.1.1
# sqlalchemy: 2.0.28
# python-dotenv: 1.0.1