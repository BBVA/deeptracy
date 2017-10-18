Deploy deeptracy
================

This folder contains *an example* of how to deploy deeptracy with terraform and docker-compose in AWS EC2

You need valid credentials for terraform in your environment and a **pem** file to create the instance for the deployment.

This example also assume that you want to configure deeptracy to be able to pull private repositories with *LOCAL_PRIVATE_KEY*
aut type. For that you need a valid key to be able to pull them.

What you need:
--------------

- `deeptracy.pem` file in this folder to have access to the created EC2 instance. If your key name is not deeptracy you need to update the `instance.tf` file.

- `id_rsa` file in this folder to have access to pull private repositories with that key. If you dont want to pull private repos you can comment the provisioner part in `instance.tf` file that copies that key to the EC2 instance.

- Valid AWS credentials for terraform in your environment

Usage
-----

.. code:: bash

    $ cd deploy
    $ terraform plan
    $ terraform apply

Before plan & apply your instance should spin up and in a few minutes deeptracy should be ready to accept requests in port `80`
