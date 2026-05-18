def compare_scan_results(result1, result2):
    def _issue_key(issue):
        return (issue.get('filename', ''), issue.get('line_number', 0), issue.get('test_name', ''))
    results1 = result1.get('results', []) if result1 else []
    results2 = result2.get('results', []) if result2 else []
    issues1 = {_issue_key(i): i for i in results1}
    issues2 = {_issue_key(i): i for i in results2}
    keys1 = set(issues1.keys())
    keys2 = set(issues2.keys())
    new = [issues2[k] for k in (keys2 - keys1)]
    fixed = [issues1[k] for k in (keys1 - keys2)]
    persistent = [issues1[k] for k in (keys1 & keys2)]
    return {
        "new": new,
        "fixed": fixed,
        "persistent": persistent
    }