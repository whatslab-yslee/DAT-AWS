resource "aws_route_table_association" "tfer--subnet-0234d2d0f023527b9" {
  route_table_id = "${data.terraform_remote_state.route_table.outputs.aws_route_table_tfer--rtb-08313f02fc1ab55dc_id}"
  subnet_id      = "${data.terraform_remote_state.subnet.outputs.aws_subnet_tfer--subnet-0234d2d0f023527b9_id}"
}

resource "aws_route_table_association" "tfer--subnet-055459420f58170e3" {
  route_table_id = "${data.terraform_remote_state.route_table.outputs.aws_route_table_tfer--rtb-08313f02fc1ab55dc_id}"
  subnet_id      = "${data.terraform_remote_state.subnet.outputs.aws_subnet_tfer--subnet-055459420f58170e3_id}"
}

resource "aws_route_table_association" "tfer--subnet-0a1f590b9cf952f7e" {
  route_table_id = "${data.terraform_remote_state.route_table.outputs.aws_route_table_tfer--rtb-07b0eb1073e6923ab_id}"
  subnet_id      = "${data.terraform_remote_state.subnet.outputs.aws_subnet_tfer--subnet-0a1f590b9cf952f7e_id}"
}

resource "aws_route_table_association" "tfer--subnet-0c8f4423b6c20d70c" {
  route_table_id = "${data.terraform_remote_state.route_table.outputs.aws_route_table_tfer--rtb-07b0eb1073e6923ab_id}"
  subnet_id      = "${data.terraform_remote_state.subnet.outputs.aws_subnet_tfer--subnet-0c8f4423b6c20d70c_id}"
}
