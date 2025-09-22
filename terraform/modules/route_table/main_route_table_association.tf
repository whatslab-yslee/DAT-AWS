resource "aws_main_route_table_association" "tfer--vpc-02c43b9a4ec12529a" {
  route_table_id = "${data.terraform_remote_state.route_table.outputs.aws_route_table_tfer--rtb-0f5b39295837484f9_id}"
  vpc_id         = "${data.terraform_remote_state.vpc.outputs.aws_vpc_tfer--vpc-02c43b9a4ec12529a_id}"
}

resource "aws_main_route_table_association" "tfer--vpc-0379f04fb87dce2c8" {
  route_table_id = "${data.terraform_remote_state.route_table.outputs.aws_route_table_tfer--rtb-02c26d2b0411ba367_id}"
  vpc_id         = "${data.terraform_remote_state.vpc.outputs.aws_vpc_tfer--vpc-0379f04fb87dce2c8_id}"
}
