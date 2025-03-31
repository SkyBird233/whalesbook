from fire import Fire
from .cli_options import Options

def cli():
    Fire(Options)

if __name__ == "__main__":
    cli()