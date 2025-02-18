import csv
import os

class TokenUsageTracker:
    def __init__(self):
        self.current_operation = None
        self.operations = {}
        self.current_model = None

    def start_operation(self, operation_name: str):
        self.current_operation = operation_name
        if operation_name not in self.operations:
            self.operations[operation_name] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "model": None
            }

    def add_usage(self, input_tokens: int, output_tokens: int, model: str):
        if self.current_operation:
            self.operations[self.current_operation]["input_tokens"] += input_tokens
            self.operations[self.current_operation]["output_tokens"] += output_tokens
            self.operations[self.current_operation]["model"] = model

    def end_operation(self):
        if self.current_operation:
            # Write the total usage for this operation to CSV
            operation = self.operations[self.current_operation]
            with open("usage.csv", mode="a", newline="") as file:
                writer = csv.writer(file)
                if not os.path.isfile("usage.csv"):
                    writer.writerow(["operation", "model", "input_tokens", "output_tokens"])
                writer.writerow([
                    self.current_operation,
                    operation["model"],
                    operation["input_tokens"],
                    operation["output_tokens"]
                ])
            # Reset the counters for this operation
            self.operations[self.current_operation] = {
                "input_tokens": 0,
                "output_tokens": 0,
                "model": None
            }
            self.current_operation = None