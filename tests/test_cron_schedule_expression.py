import pytz
from datetime import datetime, tzinfo
from aws_cfn_update.cron_schedule_expression_updater import (
    aws_cron_pattern,
    CronScheduleExpressionUpdater as Updater,
)
from aws_cfn_update.cron_schedule_expression_updater import (
    correct_for_utc,
    correct_cron_hours_expression_for_utc,
    correct_cron_expression_for_utc,
)


def test_cron_pattern_match():
    description = """
    run every hour cron(0 4 * * * *)
    """
    assert aws_cron_pattern.search(description)


def test_hour_correct_for_utc():
    summer = pytz.timezone("Europe/Berlin").localize(datetime(2018, 8, 1))

    assert 22 == correct_for_utc(0, summer.utcoffset())
    assert 23 == correct_for_utc(1, summer.utcoffset())
    assert 0 == correct_for_utc(2, summer.utcoffset())
    assert 10 == correct_for_utc(12, summer.utcoffset())
    assert 21 == correct_for_utc(23, summer.utcoffset())

    winter = pytz.timezone("Europe/Berlin").localize(datetime(2018, 12, 1))

    assert 23 == correct_for_utc(0, winter.utcoffset())
    assert 0 == correct_for_utc(1, winter.utcoffset())
    assert 1 == correct_for_utc(2, winter.utcoffset())
    assert 11 == correct_for_utc(12, winter.utcoffset())
    assert 22 == correct_for_utc(23, winter.utcoffset())


def test_correct_cron_hours_expression_for_utc():
    summer = pytz.timezone("Europe/Berlin").localize(datetime(2018, 8, 1))

    assert "*" == correct_cron_hours_expression_for_utc("*", summer.utcoffset())
    assert "?" == correct_cron_hours_expression_for_utc("?", summer.utcoffset())
    assert "20" == correct_cron_hours_expression_for_utc("22", summer.utcoffset())
    assert "20/3" == correct_cron_hours_expression_for_utc("22/3", summer.utcoffset())
    assert "7-15" == correct_cron_hours_expression_for_utc("9-17", summer.utcoffset())
    assert "23,1,8,11" == correct_cron_hours_expression_for_utc(
        "1,3,10,13", summer.utcoffset()
    )

    winter = pytz.timezone("Europe/Berlin").localize(datetime(2018, 12, 1))

    assert "*" == correct_cron_hours_expression_for_utc("*", winter.utcoffset())
    assert "?" == correct_cron_hours_expression_for_utc("?", winter.utcoffset())
    assert "21" == correct_cron_hours_expression_for_utc("22", winter.utcoffset())
    assert "21/3" == correct_cron_hours_expression_for_utc("22/3", winter.utcoffset())
    assert "8-16" == correct_cron_hours_expression_for_utc("9-17", winter.utcoffset())
    assert "0,2,9,12" == correct_cron_hours_expression_for_utc(
        "1,3,10,13", winter.utcoffset()
    )


def test_correct_cron_expression_for_utc():
    timezone = pytz.timezone("Europe/Berlin")
    summer = timezone.localize(datetime(2018, 8, 1))

    assert "* * * * * *" == correct_cron_expression_for_utc("* * * * * *", summer)
    assert "* 2 * * * *" == correct_cron_expression_for_utc("* 4 * * * *", summer)
    assert "* 7-15 * * * *" == correct_cron_expression_for_utc("* 9-17 * * * *", summer)
    assert "* 23/3 * * * *" == correct_cron_expression_for_utc("* 1/3 * * * *", summer)
    assert "* 23/3 * * ? *" == correct_cron_expression_for_utc("* 1/3 * * ? *", summer)
    assert "* 23/3 ? * ? *" == correct_cron_expression_for_utc("* 1/3 ? * ? *", summer)
    assert "* 23/3 ? * SUN *" == correct_cron_expression_for_utc(
        "* 1/3 ? * SUN *", summer
    )


def test_template_update():
    template = {
        "Resources": {
            "Schedule": {
                "Type": "AWS::Events::Rule",
                "Properties": {
                    "Description": "Run every hour - cron(0 1/3 * * * *)",
                    "ScheduleExpression": "cron(Minutes Hours Day-of-month Month Day-of-week Year)",
                },
            }
        }
    }
    updater = Updater()
    updater.template = template
    updater.timezone = pytz.timezone("Europe/Amsterdam")
    updater.today = datetime(2018, 8, 1)
    updater.update_template()
    assert updater.dirty
    properties = template.get("Resources").get("Schedule").get("Properties")
    assert properties["ScheduleExpression"] == "cron(0 23/3 * * * *)"


def test_template_update_incorrect_cron():
    template = {
        "Resources": {
            "Schedule": {
                "Type": "AWS::Events::Rule",
                "Properties": {
                    "Description": "Run every hour - cron(1/3 * * * *)",
                    "ScheduleExpression": "cron(Minutes Hours Day-of-month Month Day-of-week Year)",
                },
            }
        }
    }
    updater = Updater()
    updater.template = template
    updater.timezone = pytz.timezone("Europe/Amsterdam")
    updater.today = datetime(2018, 8, 1)
    updater.update_template()
    assert not updater.dirty
    properties = template.get("Resources").get("Schedule").get("Properties")
    assert (
        properties["ScheduleExpression"]
        == "cron(Minutes Hours Day-of-month Month Day-of-week Year)"
    )
