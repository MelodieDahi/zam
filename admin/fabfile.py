from hashlib import md5
from pathlib import Path
from shlex import quote

from invoke import task


def sudo_put(ctx, local, remote, chown=None):
    tmp = str(Path("/tmp") / md5(remote.encode()).hexdigest())
    ctx.put(local, tmp)
    ctx.sudo(f"mv {quote(tmp)} {quote(remote)}")
    if chown:
        ctx.sudo(f"chown {chown}: {quote(remote)}")


def put_dir(ctx, local, remote, chown=None):
    local = Path(local)
    remote = Path(remote)
    for path in local.rglob("*"):
        relative_path = path.relative_to(local)
        if str(relative_path).startswith("."):
            # Avoid pushing hidden files.
            continue
        if path.is_dir():
            ctx.sudo(f"mkdir -p {quote(remote / relative_path)}")
        else:
            sudo_put(ctx, str(path), str(remote / relative_path), chown)


@task
def system(ctx):
    ctx.sudo("apt update")
    ctx.sudo("apt install -y python3.6 nginx")
    ctx.sudo("mkdir -p /srv/zam")
    ctx.sudo("mkdir -p /srv/zam/letsencrypt/.well-known/acme-challenge")
    ctx.sudo("useradd -N zam -d /srv/zam/ || exit 0")
    ctx.sudo("chown zam:users /srv/zam/")
    ctx.sudo("chsh -s /bin/bash zam")


@task
def http(ctx):
    sudo_put(ctx, "letsencrypt.conf", "/etc/nginx/snippets/letsencrypt.conf")
    sudo_put(ctx, "ssl.conf", "/etc/nginx/snippets/ssl.conf")
    certif = "/etc/letsencrypt/live/zam.beta.gouv.fr/fullchain.pem"
    exists = ctx.run('if [ -f "{}" ]; then echo 1; fi'.format(certif))
    if exists.stdout:
        conf = "nginx-https.conf"
    else:
        # Before letsencrypt.
        conf = "nginx-http.conf"
    sudo_put(ctx, conf, "/etc/nginx/sites-available/default")
    ctx.sudo("systemctl restart nginx")


@task
def bootstrap(ctx):
    system(ctx)
    http(ctx)
    letsencrypt(ctx)
    basicauth(ctx)
    # Now put the https ready Nginx conf.
    http(ctx)


@task
def basicauth(ctx):
    ctx.sudo("apt update")
    ctx.sudo("apt install -y apache2-utils")
    # Will prompt for password.
    ctx.sudo("htpasswd -c /etc/nginx/.htpasswd demozam")


@task
def letsencrypt(ctx):
    ctx.sudo("add-apt-repository ppa:certbot/certbot")
    ctx.sudo("apt update")
    ctx.sudo("apt install -y certbot software-properties-common")
    sudo_put(ctx, "certbot.ini", "/srv/zam/certbot.ini")
    sudo_put(ctx, "ssl-renew", "/etc/cron.weekly/ssl-renew")
    ctx.sudo("chmod +x /etc/cron.weekly/ssl-renew")
    ctx.sudo(
        "certbot certonly -c /srv/zam/certbot.ini --non-interactive " "--agree-tos"
    )


@task
def sshkeys(ctx):
    for name, key in ctx.config.get("ssh_keys", {}).items():
        ctx.run(
            'grep -q -r "{key}" .ssh/authorized_keys '
            '|| echo "{key}" '
            "| sudo tee --append .ssh/authorized_keys".format(key=key)
        )


@task
def deploy(ctx, source):
    put_dir(ctx, quote(source), "/srv/zam/", chown="zam")
