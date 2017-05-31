from invoke import task


@task
def test(ctx):
    ctx.run("PYTHONPATH=application:$PYTHONPATH python -m nose")