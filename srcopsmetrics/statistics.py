from typing import Dict

from srcopsmetrics.entity_schema import IssueSchema, PullRequestSchema


class Statistics:

    def __init__(self, analysed_entities):
        self.analysed_entities = analysed_entities

    def overall_entities_status(self) -> Dict[str, int]:
        statuses = {}
        for entity in self.analysed_entities:
            if entity['status'] not in self.analysed_entities.keys():
                statuses[entity['status']] = 0
            statuses[entity['status']] += 1
        return statuses
