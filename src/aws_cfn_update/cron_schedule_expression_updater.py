#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#   Copyright 2018 binx.io B.V.
import re
import sys
from datetime import datetime, timedelta, tzinfo

from croniter import croniter
from tzlocal import get_localzone

from .cfn_updater import CfnUpdater


class CronScheduleExpressionUpdater(CfnUpdater):
    """
        Updates the schedule expression of an AWS::Events::Rules resources to reflect the
        scheduled time in UTC. The required cron rule is taken from the description. It will
        update the following resource definition from:

    \b
          DailyTaskSchedule:
            Type: AWS::Events::Rule
            Properties:
              Description: run daily - cron(30 01 * * ? *)
              Name: run daily
              ScheduleExpression: cron(30 01 * * ? *)
              State: ENABLED

    to

    \b
          DailyTaskSchedule:
            Type: AWS::Events::Rule
            Properties:
              Description: run daily - cron(30 01 * * ? *)
              Name: run daily
              ScheduleExpression: cron(30 23 * * ? *)
              State: ENABLED

    with --timezone Europe/Amsterdam and --date 2018-08-01. If the updater is run with --date 2018-12-01, it
    will change it to:

    \b
          DailyTaskSchedule:
            Type: AWS::Events::Rule
            Properties:
              Description: run daily - cron(30 01 * * ? *)
              Name: run daily
              ScheduleExpression: cron(30 00 * * ? *)
              State: ENABLED


    """

    def __init__(self):
        super(CronScheduleExpressionUpdater, self).__init__()
        self._timezone = get_localzone()

        self._today = datetime.now()
        self.verbose = False
        self.dry_run = False

    @property
    def timezone(self):
        return self._timezone

    @timezone.setter
    def timezone(self, timezone):
        self._timezone = timezone
        self._today = timezone.localize(self._today)

    @property
    def today(self):
        return self._today

    @today.setter
    def today(self, dt):
        if dt.tzinfo:
            self._today = dt.replace(tzinfo=self.timezone)
        else:
            self._today = self.timezone.localize(dt)

    def is_matching_resource(self, resource):
        aws_type = resource.get("Type", "")
        description = resource.get("Properties", {}).get("Description", "")
        expression = resource.get("Properties", {}).get("ScheduleExpression", None)

        if aws_type == "AWS::Events::Rule" and aws_cron_pattern.search(description):
            return expression is None or aws_cron_pattern.search(expression)

        return False

    def all_matching_resources(self, resources):
        return {k: v for k, v in resources.items() if self.is_matching_resource(v)}

    def update_template(self):
        """
        converts the cron expression in `Description` into a UTC expression in `ScheduleExpression`.
        """
        resources = self.all_matching_resources(self.template.get("Resources", {}))

        for name, resource in resources.items():
            description = resource.get("Properties", {}).get("Description", "")
            match = aws_cron_pattern.search(description)
            if match:
                expression = "{minutes} {hours} {day_of_month} {month} {day_of_week} {year}".format(
                    **match.groupdict()
                )
                new_expression = correct_cron_expression_for_utc(expression, self.today)
                if expression != new_expression:
                    properties = resource.get("Properties")
                    properties["ScheduleExpression"] = "cron({})".format(new_expression)
                    if self.verbose:
                        print("INFO: updating {}".format(name))
                    self.dirty = True

    def main(self, tz, date, dry_run, verbose, paths):
        self.dry_run = dry_run
        self.verbose = verbose
        self.timezone = tz
        if date:
            self.today = date
        self.update(paths)


aws_cron_pattern = re.compile(
    r"cron\s*\(\s*(?P<minutes>[^\s]*)\s*(?P<hours>[^\s]*)\s*(?P<day_of_month>[^\s]*)\s*(?P<month>[^\s]*)\s*(?P<day_of_week>[^\s]*)\s*(?P<year>[^\s\)]*)\)"
)
cron_pattern = re.compile(
    r"\s*(?P<minutes>[^\s]*)\s*(?P<hours>[^\s]*)\s*(?P<day_of_month>[^\s]*)\s*(?P<month>[^\s]*)\s*(?P<day_of_week>[^\s]*)\s*(?P<year>[^\s\)]*)"
)


def correct_for_utc(hour, utcoffset):
    if utcoffset.seconds % 3600 == 0:
        return int((hour + 24 - (utcoffset.seconds / 3600)) % 24)
    else:
        raise ValueError("UTC offset is not a multiple of hours.")


def correct_cron_hours_expression_for_utc(expression, utcoffset):
    if expression == "*" or expression == "?":
        return expression

    range = re.match(r"([0-9]+)-([0-9]+)", expression)
    if range:
        from_hour = int(range.group(1))
        to_hour = int(range.group(2))
        return "{}-{}".format(
            correct_for_utc(from_hour, utcoffset), correct_for_utc(to_hour, utcoffset)
        )

    repeat = re.match(r"([0-9]+)/([0-9]+)", expression)
    if repeat:
        from_hour = int(repeat.group(1))
        repetition = int(repeat.group(2))
        return "{}/{}".format(correct_for_utc(from_hour, utcoffset), repetition)

    hours = list(filter(lambda n: re.match(r"[0-9]+", n), expression.split(",")))
    if len(hours) == len(expression.split(",")):
        hours = list(
            map(lambda h: "{}".format(correct_for_utc(int(h), utcoffset)), hours)
        )
        return ",".join(hours)
    else:
        assert False, "unsupported hour format {}".format(expression)

    return expression


def correct_cron_expression_for_utc(expression, today):
    match = cron_pattern.search(expression)
    assert match, '"{}" is not a cron expression'.format(expression)

    cron = match.groupdict()
    tomorrow_midnight = today.tzinfo.localize(
        datetime(today.year, today.month, today.day) + timedelta(days=1)
    )

    try:
        ccron = {k: ("*" if v == "?" else v) for (k, v) in cron.items()}
        expression = (
            "{minutes} {hours} {day_of_month} {month} {day_of_week} {year}".format(
                **ccron
            )
        )
        next_time = croniter(expression, tomorrow_midnight).get_next(datetime)
    except ValueError as e:
        sys.stderr.write("ERROR: {}".format(e))
        sys.exit(1)

    utcoffset = next_time.tzinfo.utcoffset(next_time)
    if utcoffset.seconds % 3600 == 0:
        cron["hours"] = correct_cron_hours_expression_for_utc(cron["hours"], utcoffset)
        expression = (
            "{minutes} {hours} {day_of_month} {month} {day_of_week} {year}".format(
                **cron
            )
        )
    else:
        sys.stderr.write(
            'WARN: UTC offset for "{}" in timezone "{}" is not a multiple of hours but {} seconds.\n'.format(
                expression, today.tzinfo, utcoffset.seconds
            )
        )

    return expression
