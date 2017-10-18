resource "aws_security_group" "allow_http" {
  name        = "allow_http"
  description = "Allow http inbound traffic"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags {
    Name = "deeptracy"
  }
}

data "template_file" "init_deeptracy" {
  template = "${file("./init.sh")}"
}

resource "aws_instance" "deeptracy" {
  ami                         = "ami-eed00d97"
  instance_type               = "t2.medium"
  user_data                   = "${data.template_file.init_deeptracy.rendered}"
  associate_public_ip_address = true
  key_name                    = "deeptracy"
  vpc_security_group_ids      = ["${aws_security_group.allow_http.id}", "sg-cf30d2a0"]

  root_block_device {
    volume_size = "20"
  }

  provisioner "file" {
    source      = "docker-compose.yml"
    destination = "/tmp/docker-compose.yml"

    connection {
      user        = "ubuntu"
      private_key = "${file("~/.ssh/deeptracy.pem")}"
    }
  }

  provisioner "file" {
    source      = "~/.ssh/bbva_bitbucket_rsa"
    destination = "/tmp/id_rsa"

    connection {
      user        = "ubuntu"
      private_key = "${file("~/.ssh/deeptracy.pem")}"
    }
  }

  tags {
    Name = "deeptracy"
  }
}

output "public_ip" {
  value = "${aws_instance.deeptracy.public_ip}"
}
