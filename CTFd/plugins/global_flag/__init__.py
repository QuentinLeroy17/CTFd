from flask import Blueprint, request, jsonify, abort

from CTFd.plugins import register_plugin_assets_directory, register_plugin_script
from CTFd.models import Challenges, Flags, Solves
from CTFd.plugins.flags import get_flag_class, FlagException
from CTFd.plugins.challenges import get_chal_class
from CTFd.cache import clear_standings, clear_challenges
from CTFd.utils.user import authed, get_current_team, get_current_user
from CTFd.utils import config

blueprint = Blueprint('global_flag', __name__, template_folder='templates', static_folder='assets')


@blueprint.route('/plugins/global_flag/submit', methods=['POST'])
def submit_flag():
    if not authed():
        return jsonify({'success': True, 'data': {'status': 'authentication_required'}}), 403

    data = request.get_json() if request.is_json else request.form
    submission = data.get('submission', '').strip()
    user = get_current_user()
    team = get_current_team()

    if config.is_teams_mode() and team is None:
        abort(403)

    for flag in Flags.query.all():
        challenge = Challenges.query.filter_by(id=flag.challenge_id).first()
        if challenge.state in ('hidden', 'locked'):
            continue
        try:
            if get_flag_class(flag.type).compare(flag, submission):
                chal_class = get_chal_class(challenge.type)
                solved = Solves.query.filter_by(account_id=user.account_id, challenge_id=challenge.id).first()
                if solved:
                    return jsonify({'success': True, 'data': {'status': 'already_solved', 'challenge': challenge.name, 'challenge_id': challenge.id}})

                chal_class.solve(user=user, team=team, challenge=challenge, request=request)
                clear_standings()
                clear_challenges()
                return jsonify({'success': True, 'data': {'status': 'correct', 'challenge': challenge.name, 'challenge_id': challenge.id}})
        except FlagException as e:
            return jsonify({'success': False, 'errors': str(e)}), 400

    return jsonify({'success': True, 'data': {'status': 'incorrect'}})


def load(app):
    register_plugin_assets_directory(app, base_path='/plugins/global_flag/assets/')
    register_plugin_script('/plugins/global_flag/assets/flag_submit.js')
    app.register_blueprint(blueprint)
