"""

"""


class AutoImport:
    def __getattr__(self, name: str, /):
        import importlib
        return importlib.import_module(name)

auto = AutoImport()


APPDIR = auto.pathlib.Path.cwd()


def Poincare(
    *,
    seeds: list[tuple[float, float]],
    punctures: int,
    step: float,
) -> auto.pandas.DataFrame:
    with auto.tempfile.TemporaryDirectory() as tmp:
        tmp = auto.pathlib.Path(tmp)

        fifo = tmp / 'mkfifo'
        auto.os.mkfifo(fifo)

        output = tmp / 'output'
        output.mkdir(parents=True, exist_ok=True)

        csv = output.with_suffix('.csv')
        if csv.exists():
            print(f'Unexpected: The CSV {csv!r} exists; removing it')
            csv.unlink()

        args = [
            APPDIR/"vtkm/build/examples/poincare/Poincare",
            '--dir', "/mnt/seenas2/data/xgc/poincare/dropbox",
            '--3DFile', "xgc.3d.00450.bp",
            '--CoeffFile', "xgc.bfield.bp",
            '--output', output.name,
            '--interactive',
            '--mkfifoName', fifo,
            '--openmp',
            '--numPunc', '10',
            '--stepSize', '0.1',
        ]

        print(auto.shlex.join( map(str, args) ))

        with auto.subprocess.Popen(args, cwd=tmp) as process:
            with open(fifo, 'rt', encoding='ascii') as f:
                print(f.read())  # should be "ready"

            with open(fifo, 'wt', encoding='ascii') as f:
                auto.np.savetxt(f, seeds, fmt='%f')

                numPunc = punctures
                stepSize = step
                print(f';{numPunc :d} {stepSize :f}', file=f, flush=True)

            with open(fifo, 'rt', encoding='ascii') as f:
                print(f.read())  # should be "done"

            for _ in range(100):
                if csv.exists():
                    break
                auto.time.sleep(0.5)
            else:
                print(f'Error: The CSV was never created')

            # auto.time.sleep(10)
            process.kill()
        #/with process

        # !ls -lahR "$tmp"

        return auto.pandas.read_csv(output.with_suffix('.csv'))
    #/ with tmp
#/ def Poincare


app = auto.flask.Flask(__name__)
KEY = '904e6837-ee8d-4c63-ae06-413e267333bd'

@app.route('/api/poincare/', methods=['POST'])
def poincare() -> auto.flask.Response:
    # seeds from POST body
    seeds = auto.flask.request.get_json()
    # seeds = [tuple(seed) for seed in seeds]

    # params from query string
    punctures = int(auto.flask.request.args.get('punctures', 10))
    step = float(auto.flask.request.args.get('step', 0.1))
    key = auto.flask.request.args.get('key', None)

    if key != KEY:
        return 'Not Authorized', 403

    # run poincare
    df = Poincare(seeds=seeds, punctures=punctures, step=step)

    # return csv
    return auto.flask.Response(
        df.to_csv(index=False),
        mimetype='text/csv',
    )
#/ def poincare


def main(bind: str, port: int):
    print(f'Listening on http://{bind}:{port}...')

    app.run(
        host=bind,
        port=port,
    )


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--bind', default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8080)
    args = vars(parser.parse_args())

    main(**args)


if __name__ == '__main__':
    cli()
