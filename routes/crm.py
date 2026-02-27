from flask import Blueprint, render_template

from queries.crm import (
    contact_count,
    company_count,
    deal_count,
    high_value_count,
    stale_count,
    pipeline_value,
    pending_drafts_count,
    contacts_with_scores,
    companies_list,
    deals_list,
    pending_drafts,
    last_sync,
    score_distribution,
)

bp = Blueprint("crm", __name__)


@bp.route("/crm")
def crm_index():
    return render_template(
        "crm.html",
        active_page="crm",
        contacts=contact_count(),
        companies=company_count(),
        deals=deal_count(),
        high_value=high_value_count(),
        stale=stale_count(),
        pipeline=pipeline_value(),
        drafts_count=pending_drafts_count(),
        contacts_table=contacts_with_scores(),
        companies_table=companies_list(),
        deals_table=deals_list(),
        drafts_table=pending_drafts(),
        sync=last_sync(),
        distribution=score_distribution(),
    )
