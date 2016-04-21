from datetime import datetime
from szurubooru import db

def test_saving_post(post_factory, user_factory, tag_factory):
    user = user_factory()
    tag1 = tag_factory()
    tag2 = tag_factory()
    related_post1 = post_factory()
    related_post2 = post_factory()
    post = db.Post()
    post.safety = 'safety'
    post.type = 'type'
    post.checksum = 'deadbeef'
    post.creation_time = datetime(1997, 1, 1)
    post.last_edit_time = datetime(1998, 1, 1)
    db.session.add_all([user, tag1, tag2, related_post1, related_post2, post])

    post.user = user
    post.tags.append(tag1)
    post.tags.append(tag2)
    post.relations.append(related_post1)
    post.relations.append(related_post2)
    db.session.commit()

    db.session.refresh(post)
    assert not db.session.dirty
    assert post.user.user_id is not None
    assert post.safety == 'safety'
    assert post.type == 'type'
    assert post.checksum == 'deadbeef'
    assert post.creation_time == datetime(1997, 1, 1)
    assert post.last_edit_time == datetime(1998, 1, 1)
    assert len(post.relations) == 2

def test_cascade_deletions(post_factory, user_factory, tag_factory):
    user = user_factory()
    tag1 = tag_factory()
    tag2 = tag_factory()
    related_post1 = post_factory()
    related_post2 = post_factory()
    post = post_factory()
    db.session.add_all([user, tag1, tag2, post, related_post1, related_post2])
    db.session.flush()

    post.user = user
    post.tags.append(tag1)
    post.tags.append(tag2)
    post.relations.append(related_post1)
    post.relations.append(related_post2)
    db.session.flush()

    assert not db.session.dirty
    assert post.user.user_id is not None
    assert len(post.relations) == 2
    assert db.session.query(db.User).count() == 1
    assert db.session.query(db.Tag).count() == 2
    assert db.session.query(db.Post).count() == 3
    assert db.session.query(db.PostTag).count() == 2
    assert db.session.query(db.PostRelation).count() == 2

    db.session.delete(post)
    db.session.commit()

    assert not db.session.dirty
    assert db.session.query(db.User).count() == 1
    assert db.session.query(db.Tag).count() == 2
    assert db.session.query(db.Post).count() == 2
    assert db.session.query(db.PostTag).count() == 0
    assert db.session.query(db.PostRelation).count() == 0

def test_tracking_tag_count(post_factory, tag_factory):
    post = post_factory()
    tag1 = tag_factory()
    tag2 = tag_factory()
    db.session.add_all([tag1, tag2, post])
    db.session.flush()
    post.tags.append(tag1)
    post.tags.append(tag2)
    db.session.commit()
    assert len(post.tags) == 2
    assert post.tag_count == 2
    db.session.delete(tag1)
    db.session.commit()
    db.session.refresh(post)
    assert len(post.tags) == 1
    assert post.tag_count == 1
    db.session.delete(tag2)
    db.session.commit()
    db.session.refresh(post)
    assert len(post.tags) == 0
    assert post.tag_count == 0