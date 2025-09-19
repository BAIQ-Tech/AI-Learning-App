"""Add medium priority features

Revision ID: 002_add_medium_priority_features
Revises: 001_initial_migration
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_medium_priority_features'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade():
    # Create gamification tables
    op.create_table('achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('requirements', sa.JSON(), nullable=False),
        sa.Column('points', sa.Integer(), nullable=True),
        sa.Column('rarity', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_achievements_id'), 'achievements', ['id'], unique=False)
    
    op.create_table('user_achievements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('achievement_id', sa.Integer(), nullable=False),
        sa.Column('earned_at', sa.DateTime(), nullable=True),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['achievement_id'], ['achievements.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_achievements_id'), 'user_achievements', ['id'], unique=False)
    
    op.create_table('user_streaks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('current_streak', sa.Integer(), nullable=True),
        sa.Column('longest_streak', sa.Integer(), nullable=True),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('streak_freeze_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_streaks_id'), 'user_streaks', ['id'], unique=False)
    
    op.create_table('user_levels',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('current_level', sa.Integer(), nullable=True),
        sa.Column('total_xp', sa.Integer(), nullable=True),
        sa.Column('xp_to_next_level', sa.Integer(), nullable=True),
        sa.Column('level_progress', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_levels_id'), 'user_levels', ['id'], unique=False)
    
    op.create_table('leaderboards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('category', sa.String(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=True),
        sa.Column('rank', sa.Integer(), nullable=True),
        sa.Column('period_start', sa.DateTime(), nullable=False),
        sa.Column('period_end', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_leaderboards_id'), 'leaderboards', ['id'], unique=False)
    
    op.create_table('daily_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('challenge_type', sa.String(), nullable=False),
        sa.Column('difficulty', sa.String(), nullable=True),
        sa.Column('requirements', sa.JSON(), nullable=False),
        sa.Column('reward_xp', sa.Integer(), nullable=True),
        sa.Column('reward_points', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('date', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_daily_challenges_id'), 'daily_challenges', ['id'], unique=False)
    
    op.create_table('user_daily_challenges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('challenge_id', sa.Integer(), nullable=False),
        sa.Column('progress', sa.Integer(), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['challenge_id'], ['daily_challenges.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_daily_challenges_id'), 'user_daily_challenges', ['id'], unique=False)
    
    op.create_table('user_rewards',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reward_type', sa.String(), nullable=False),
        sa.Column('reward_value', sa.Integer(), nullable=False),
        sa.Column('reward_data', sa.JSON(), nullable=True),
        sa.Column('source', sa.String(), nullable=False),
        sa.Column('earned_at', sa.DateTime(), nullable=True),
        sa.Column('is_used', sa.Boolean(), nullable=True),
        sa.Column('used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_rewards_id'), 'user_rewards', ['id'], unique=False)
    
    # Create social learning tables
    op.create_table('study_groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('max_members', sa.Integer(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_groups_id'), 'study_groups', ['id'], unique=False)
    
    op.create_table('study_group_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['study_groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_group_members_id'), 'study_group_members', ['id'], unique=False)
    
    op.create_table('study_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('session_type', sa.String(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('max_participants', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['group_id'], ['study_groups.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_sessions_id'), 'study_sessions', ['id'], unique=False)
    
    op.create_table('study_session_participants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), nullable=True),
        sa.Column('left_at', sa.DateTime(), nullable=True),
        sa.Column('participation_score', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['session_id'], ['study_sessions.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_study_session_participants_id'), 'study_session_participants', ['id'], unique=False)
    
    op.create_table('peer_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user1_id', sa.Integer(), nullable=False),
        sa.Column('user2_id', sa.Integer(), nullable=False),
        sa.Column('user1_language', sa.String(), nullable=False),
        sa.Column('user2_language', sa.String(), nullable=False),
        sa.Column('compatibility_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user1_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['user2_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peer_matches_id'), 'peer_matches', ['id'], unique=False)
    
    op.create_table('peer_conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('match_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('message_type', sa.String(), nullable=True),
        sa.Column('media_url', sa.String(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['match_id'], ['peer_matches.id'], ),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_peer_conversations_id'), 'peer_conversations', ['id'], unique=False)
    
    op.create_table('mentorship_programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mentor_id', sa.Integer(), nullable=False),
        sa.Column('mentee_id', sa.Integer(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('start_date', sa.DateTime(), nullable=True),
        sa.Column('end_date', sa.DateTime(), nullable=True),
        sa.Column('goals', sa.JSON(), nullable=True),
        sa.Column('progress_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['mentee_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['mentor_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentorship_programs_id'), 'mentorship_programs', ['id'], unique=False)
    
    op.create_table('mentorship_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('session_type', sa.String(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['mentorship_programs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentorship_sessions_id'), 'mentorship_sessions', ['id'], unique=False)
    
    op.create_table('content_shares',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('content_data', sa.JSON(), nullable=False),
        sa.Column('language_code', sa.String(), nullable=False),
        sa.Column('difficulty_level', sa.String(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('likes_count', sa.Integer(), nullable=True),
        sa.Column('shares_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_shares_id'), 'content_shares', ['id'], unique=False)
    
    op.create_table('content_likes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content_shares.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_likes_id'), 'content_likes', ['id'], unique=False)
    
    op.create_table('content_comments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_id'], ['content_shares.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_comments_id'), 'content_comments', ['id'], unique=False)
    
    op.create_table('language_exchanges',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('native_language', sa.String(), nullable=False),
        sa.Column('learning_language', sa.String(), nullable=False),
        sa.Column('proficiency_level', sa.String(), nullable=False),
        sa.Column('availability', sa.JSON(), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_language_exchanges_id'), 'language_exchanges', ['id'], unique=False)
    
    op.create_table('language_exchange_matches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('exchange1_id', sa.Integer(), nullable=False),
        sa.Column('exchange2_id', sa.Integer(), nullable=False),
        sa.Column('compatibility_score', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['exchange1_id'], ['language_exchanges.id'], ),
        sa.ForeignKeyConstraint(['exchange2_id'], ['language_exchanges.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_language_exchange_matches_id'), 'language_exchange_matches', ['id'], unique=False)


def downgrade():
    # Drop social learning tables
    op.drop_index(op.f('ix_language_exchange_matches_id'), table_name='language_exchange_matches')
    op.drop_table('language_exchange_matches')
    op.drop_index(op.f('ix_language_exchanges_id'), table_name='language_exchanges')
    op.drop_table('language_exchanges')
    op.drop_index(op.f('ix_content_comments_id'), table_name='content_comments')
    op.drop_table('content_comments')
    op.drop_index(op.f('ix_content_likes_id'), table_name='content_likes')
    op.drop_table('content_likes')
    op.drop_index(op.f('ix_content_shares_id'), table_name='content_shares')
    op.drop_table('content_shares')
    op.drop_index(op.f('ix_mentorship_sessions_id'), table_name='mentorship_sessions')
    op.drop_table('mentorship_sessions')
    op.drop_index(op.f('ix_mentorship_programs_id'), table_name='mentorship_programs')
    op.drop_table('mentorship_programs')
    op.drop_index(op.f('ix_peer_conversations_id'), table_name='peer_conversations')
    op.drop_table('peer_conversations')
    op.drop_index(op.f('ix_peer_matches_id'), table_name='peer_matches')
    op.drop_table('peer_matches')
    op.drop_index(op.f('ix_study_session_participants_id'), table_name='study_session_participants')
    op.drop_table('study_session_participants')
    op.drop_index(op.f('ix_study_sessions_id'), table_name='study_sessions')
    op.drop_table('study_sessions')
    op.drop_index(op.f('ix_study_group_members_id'), table_name='study_group_members')
    op.drop_table('study_group_members')
    op.drop_index(op.f('ix_study_groups_id'), table_name='study_groups')
    op.drop_table('study_groups')
    
    # Drop gamification tables
    op.drop_index(op.f('ix_user_rewards_id'), table_name='user_rewards')
    op.drop_table('user_rewards')
    op.drop_index(op.f('ix_user_daily_challenges_id'), table_name='user_daily_challenges')
    op.drop_table('user_daily_challenges')
    op.drop_index(op.f('ix_daily_challenges_id'), table_name='daily_challenges')
    op.drop_table('daily_challenges')
    op.drop_index(op.f('ix_leaderboards_id'), table_name='leaderboards')
    op.drop_table('leaderboards')
    op.drop_index(op.f('ix_user_levels_id'), table_name='user_levels')
    op.drop_table('user_levels')
    op.drop_index(op.f('ix_user_streaks_id'), table_name='user_streaks')
    op.drop_table('user_streaks')
    op.drop_index(op.f('ix_user_achievements_id'), table_name='user_achievements')
    op.drop_table('user_achievements')
    op.drop_index(op.f('ix_achievements_id'), table_name='achievements')
    op.drop_table('achievements')
