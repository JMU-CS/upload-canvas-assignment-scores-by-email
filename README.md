# upload-canvas-assignment-scores-by-email

## Usage

The python script will give you some usage information if you just run it: `python email_based_scores_to_canvas.py`

You may find it helpful to set environment variables for your `CANVAS_KEY` (see https://canvas.instructure.com/doc/api/file.oauth.html#manual-token-generation) and `CANVAS_URL` (e.g. `https://canvas.jmu.edu/`)

In Canvas, go to your assignment page, e.g. a URL like `https://canvas.jmu.edu/courses/1700404/assignments/11413662`
The 2 integers in the URL are the course_id and assignment_id respectively. You need them in the following:

`python email_based_scores_to_canvas.py course_id assignment_id scores.csv`

so for the example it would be:

`python email_based_scores_to_canvas.py 1700404 11413662 scores.csv`

This will only print the data as it _would be_ submitted to Canvas. You must pass `--wet_run` (as in not a dry run, the default) to actually have the scores sent to canvas.

Output from a= successful run would look something like
```
OK! RESPONSE:
{"id":4310251,"context_id":1700404,"context_type":"Course","user_id":null,"tag":"submissions_update","completion":null,"workflow_state":"queued","created_at":"2020-01-07T05:27:13Z","updated_at":"2020-01-07T05:27:13Z","message":null,"url":"https://canvas.jmu.edu/api/v1/progress/4310251"}
```
