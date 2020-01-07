#!/usr/bin/env python3

from canvasapi import Canvas
from canvasapi.exceptions import ResourceDoesNotExist, InvalidAccessToken, Unauthorized
from requests.exceptions import ConnectionError, MissingSchema
import requests
import json
from collections import defaultdict
import os
import sys
import argparse
import csv

def id_to_email (login_id):
    return login_id + "@dukes.jmu.edu"


def pretty_print_POST(req):
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))

def main ():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--canvas_key",
        default=None,
        help="your canvas account token. see: https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation")

    parser.add_argument(
        "--canvas_url",
        default=None,
        help="the URL of your canvas instance, e.g. https://canvas.jmu.edu/")

    parser.add_argument("course", help="canvas course id")
    
    parser.add_argument("assignment", help="canvas assignment id")

    parser.add_argument(
        "scores", help="csv file with at least the columns: 'Email:' and 'Total:'")

    parser.add_argument(
        "--wet_run",
        action="store_true",
        help="really asign the scores")

    args = parser.parse_args()

    DRY = not args.wet_run

    canvas_key = args.canvas_key
    canvas_url = args.canvas_url
    if canvas_key is None:
        canvas_key = os.environ["CANVAS_KEY"]
    if canvas_url is None:
        canvas_url = os.environ["CANVAS_URL"]
    if canvas_key is None or canvas_url is None:
        print("must provide canvas api key and url via either the optional flags or the environment variables: CANVAS_KEY and CANVAS_URL")
        sys.exit(1)

    canvas = Canvas(canvas_url, canvas_key)
    try:
        the_course = canvas.get_course(args.course)
        students = the_course.get_recent_students()
        student_email_to_id = {}
        scores_to_submit = {}
        for student in students:
            student_email_to_id[id_to_email(student.login_id)]=student.id
        with open(args.scores, "r") as f:
            reader = csv.DictReader(f)
            fields = reader.fieldnames
            # print(fields)
            for score in reader:
                # print(score)
                scores_to_submit[student_email_to_id[score["Email:"]]] = {
                    "posted_grade": score["Total:"]
                }
        scores_to_submit = {
            "grade_data": scores_to_submit
        }

        if DRY:
            print(scores_to_submit)
        else:
            # idk what's wrong with this function that it doesn't work 
            # the_course.submissions_bulk_update(grade_data=scores_to_submit) 
            url_string = ("{}api/v1/courses/{}"
                          "/assignments/{}/submissions/update_grades")
            url = url_string.format(canvas_url, args.course,
                                    args.assignment)
            data = str.encode(json.dumps(scores_to_submit))
            header = {"Authorization": "Bearer {}".format(canvas_key),
                    "Content-Type": "application/json"}
            req = requests.Request("POST", url, data=data, headers=header)
            prepared = req.prepare()
            # pretty_print_POST(prepared)
            s = requests.Session()
            return s.send(prepared)
        


    except ResourceDoesNotExist:
        print("couldn't find course with canvas id:", args.course)
        sys.exit(1)
    except InvalidAccessToken:
        print("the access key your provided does not seem to be correct:", canvas_key)
        sys.exit(1)
    except Unauthorized:
        print("the access key your provided does not seem to have access to course:", args.course)
        sys.exit(1)
    except (ConnectionError, MissingSchema) as canvas_url_issue:
        print("--canvas_url may have been incorrect:",
              args.canvas_url, canvas_url_issue)
        sys.exit(1)

if __name__ == "__main__":
    response = main()
    if response.ok:
        # if VERBOSE:
        print("RESPONSE:")
        print(response.text)
    else:  # failure case
        print("fail")
        print(response.status_code)
