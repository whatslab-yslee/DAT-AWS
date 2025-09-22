resource "aws_lb_target_group_attachment" "tfer--arn-003A-aws-003A-elasticloadbalancing-003A-ap-northeast-2-003A-977099001606-003A-targetgroup-002F-dat-ecs-tg-002F-bd7a70be4823d1ba-10-002E-0-002E-10-002E-125" {
  target_group_arn = "arn:aws:elasticloadbalancing:ap-northeast-2:977099001606:targetgroup/dat-ecs-tg/bd7a70be4823d1ba"
  target_id        = "10.0.10.125"
}
