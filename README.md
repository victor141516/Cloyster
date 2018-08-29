# Kloyster

Host multiple private static web pages https://kloyster.tk

## Usage

Once it's deployed, you can access to `/` and upload there a ZIP file containing your web page, give a name and a password and upload it.

The name will be the path to access your web site (ex: `name=hi --> url=/hi`).

That path will be protected with the password.

## Admin

The route to manage all the sites is `/admin` (password is `admin` by default). There you can edit passwords for the other web sites or remove them.

Thi page can be replaced by removing it from the admin pane, then adding the new one as a new static web site (it must have always `admin` as name).

Admin has access to all other sites.

## Deployment

Run `docker-compose up -d` to have it working with Docker.

You should edit the file `docker-compose.yml` and add an environment variable to the `Kloyster` container: `KLOYSTER_SALT` (it's the salt to encrypt the passwords).
