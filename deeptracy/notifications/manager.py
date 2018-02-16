from deeptracy_core.dal.project.project_hooks import ProjectHookType
import deeptracy.notifications.slack_webhook_post as slack
import deeptracy.notifications.email as email


def notify_scan_results(project, scan_vulns):
    notify_to_user(project, 'Resultados del escaneo en {}'.format(project.name), scan_vulns)


def notify_deltas(project, scan_vulns):
    notify_to_user(project, 'Nuevas vulnerabilidades en tu proyecto {}'.format(project.name), scan_vulns)


def notify_to_user(project, subject: str, scan_vulns):
    if project.hook_type == ProjectHookType.SLACK_EMAIL.name:
        slack.notify(project.hook_data, subject)
        email.notify(project, subject, scan_vulns)
    elif project.hook_type == ProjectHookType.SLACK.name:
        slack.notify(project.hook_data, subject)
    elif project.hook_type == ProjectHookType.EMAIL.name:
        email.notify(project, subject, scan_vulns)
