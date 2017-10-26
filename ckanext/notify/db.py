import sqlalchemy as sa
import uuid

Channel = None
Org_Slack_Details = None
Org_Email_Details = None


def uuid4():
    return str(uuid.uuid4())


def init_db(model):

    global Channel
    global Org_Slack_Details
    global Org_Email_Details

    if Channel is None:
            class _Channel(model.DomainObject):

                @classmethod
                def get(cls, **kw):
                    '''Finds all the instances required.'''
                    query = model.Session.query(cls).autoflush(False)
                    return query.filter_by(**kw).all()

            Channel = _Channel

            channels_table = sa.Table('channels', model.meta.metadata,
                sa.Column('id', sa.types.UnicodeText, primary_key=True, default=uuid4),
                sa.Column('channel', sa.types.UnicodeText, primary_key=False, default=u'')
            )

            # Create the table only if it does not exist
            channels_table.create(checkfirst=True)

            model.meta.mapper(Channel, channels_table,)

    if Org_Slack_Details is None:
        class _Org_Slack_Details(model.DomainObject):

            @classmethod
            def get(cls, **kw):
                '''Finds all the instances required.'''
                query = model.Session.query(cls).autoflush(False)
                return query.filter_by(**kw).all()

            @classmethod
            def slack_channel_exists(cls, webhook_url, slack_channel):
                '''Returns true if there is a channel with the same webhook url and slack channel'''
                query = model.Session.query(cls).autoflush(False)
                if query.filter(cls.webhook_url == webhook_url).first() is None:
                    return False
                else:
                    return query.filter(cls.webhook_url == webhook_url)\
                        .filter(cls.slack_channel == slack_channel).first()

        Org_Slack_Details = _Org_Slack_Details

        org_slack_details_table = sa.Table('org_slack_details', model.meta.metadata,
            sa.Column('id', sa.types.UnicodeText, primary_key=True, default=uuid4),
            sa.Column('organization_id', sa.types.UnicodeText, primary_key=False, default=None),
            sa.Column('webhook_url', sa.types.UnicodeText, primary_key=False, default=u''),
            sa.Column('slack_channel', sa.types.UnicodeText, primary_key=False, default=u''),
        )

        # Creates the table only if it doesn't exist
        org_slack_details_table.create(checkfirst=True)

        model.meta.mapper(Org_Slack_Details, org_slack_details_table,)

    if Org_Email_Details is None:
        class _Org_Email_Details(model.DomainObject):

            @classmethod
            def get(cls, **kw):
                '''Finds all the instances required.'''
                query = model.Session.query(cls).autoflush(False)
                return query.filter_by(**kw).all()

            @classmethod
            def email_channel_exists(cls, email):
                '''Returns true if there is a email channel with the same webhook url'''
                query = model.Session.query(cls).autoflush(False)
                return query.filter(cls.email == email).first() is not None

        Org_Email_Details = _Org_Email_Details

        org_email_details_table = sa.Table('org_email_details', model.meta.metadata,
            sa.Column('id', sa.types.UnicodeText, primary_key=True, default=uuid4),
            sa.Column('organization_id', sa.types.UnicodeText, primary_key=False, default=None),
            sa.Column('email', sa.types.UnicodeText, primary_key=False, default=u''),
        )

        # Creates the table only if it doesn't exist
        org_email_details_table.create(checkfirst=True)

        model.meta.mapper(Org_Email_Details, org_email_details_table,)
