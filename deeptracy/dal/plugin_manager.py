# -*- coding: utf-8 -*-

from sqlalchemy.orm import Session
from deeptracy.dal.models import Plugin


def deactivate_all_plugins(session: Session):
    session.query(Plugin).update({Plugin.active: False})


def add_or_activate_plugin(name: str, lang: str, session: Session) -> Plugin:
    query = session.query(Plugin).filter(Plugin.name == name).filter(Plugin.lang == lang)
    plugin = query.first()
    if plugin is not None:
        plugin.active = True
    else:
        plugin = Plugin(name=name, lang=lang, active=True)

    session.add(plugin)
    return plugin


def get_plugins_for_lang(lang: str, session: Session):
    query = session.query(Plugin).filter(Plugin.lang == lang)
    return query.all()
