import json

import requests_async

LEETCODE_URL = "https://leetcode.com/graphql/"


async def get_solved_problems(username: str):
    query = (
        """
            query{
             matchedUser(username: "%s") {
                 submitStatsGlobal{
                     acSubmissionNum {
                        difficulty
                        count
                    }
                 }
             }
        }
        """
        % username
    )
    r = await requests_async.post(LEETCODE_URL, json={"query": query}, verify=False)
    json_data = json.loads(r.text)
    solved_problems = json_data["data"]["matchedUser"]["submitStatsGlobal"][
        "acSubmissionNum"
    ]
    return [solved_problems[i]["count"] for i in range(1, 4)]
