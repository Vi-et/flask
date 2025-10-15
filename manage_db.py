#!/usr/bin/env python3
"""
Database management CLI cho Flask app
"""

import click
from app import app, db, User, Post, Contact
from datetime import datetime

@click.group()
def cli():
    """Database management commands"""
    pass

@cli.command()
def init_db():
    """Khởi tạo database"""
    with app.app_context():
        db.create_all()
        click.echo("✅ Database tables created!")

@cli.command()  
def reset_db():
    """Reset database (xóa tất cả data)"""
    if click.confirm('⚠️  Bạn có chắc muốn xóa tất cả dữ liệu?'):
        with app.app_context():
            db.drop_all()
            db.create_all()
            click.echo("🗑️  Database đã được reset!")

@cli.command()
def seed_db():
    """Thêm dữ liệu mẫu vào database"""
    with app.app_context():
        # Kiểm tra nếu đã có data
        if User.query.count() > 0:
            if not click.confirm('Database đã có data. Tiếp tục thêm?'):
                return
        
        # Thêm users
        users_data = [
            User(name='Admin User', email='admin@example.com'),
            User(name='John Doe', email='john@example.com'),
            User(name='Jane Smith', email='jane@example.com'),
            User(name='Bob Wilson', email='bob@example.com'),
        ]
        
        for user in users_data:
            db.session.add(user)
        
        db.session.commit()
        
        # Thêm posts
        posts_data = [
            Post(
                title='Getting Started with Flask',
                content='Flask is a lightweight and powerful web framework for Python. This tutorial will guide you through the basics of Flask development, from setting up your first route to building a complete web application.',
                author_id=1
            ),
            Post(
                title='SQLAlchemy Best Practices',
                content='SQLAlchemy is the most popular ORM for Python. In this post, we will explore best practices for using SQLAlchemy in your Flask applications, including model design, query optimization, and relationship management.',
                author_id=2
            ),
            Post(
                title='Building RESTful APIs with Flask',
                content='REST APIs are essential for modern web applications. Learn how to design and implement robust RESTful APIs using Flask, including proper HTTP methods, status codes, and error handling.',
                author_id=1
            ),
            Post(
                title='Database Design Principles',
                content='Good database design is crucial for application performance and maintainability. This article covers fundamental principles of relational database design, normalization, and indexing strategies.',
                author_id=3
            ),
            Post(
                title='Frontend-Backend Communication',
                content='Understanding how frontend and backend components communicate is essential for full-stack development. We will explore different patterns and protocols for client-server communication.',
                author_id=4
            )
        ]
        
        for post in posts_data:
            db.session.add(post)
        
        db.session.commit()
        
        click.echo(f"✅ Đã thêm {len(users_data)} users và {len(posts_data)} posts!")

@cli.command()
def stats():
    """Hiển thị thống kê database"""
    with app.app_context():
        users_count = User.query.count()
        posts_count = Post.query.count()
        contacts_count = Contact.query.count()
        
        click.echo("📊 Database Statistics:")
        click.echo(f"   Users: {users_count}")
        click.echo(f"   Posts: {posts_count}")
        click.echo(f"   Contacts: {contacts_count}")
        
        # Top authors
        if posts_count > 0:
            click.echo("\n👥 Top Authors:")
            top_authors = db.session.query(
                User.name, 
                db.func.count(Post.id).label('post_count')
            ).join(Post).group_by(User.id).order_by(
                db.func.count(Post.id).desc()
            ).limit(5).all()
            
            for author, count in top_authors:
                click.echo(f"   {author}: {count} posts")

@cli.command()
@click.argument('table')
def show(table):
    """Hiển thị dữ liệu trong bảng (users, posts, contacts)"""
    with app.app_context():
        if table.lower() == 'users':
            users = User.query.all()
            click.echo(f"\n👥 Users ({len(users)}):")
            for user in users:
                click.echo(f"   ID: {user.id} | {user.name} | {user.email} | Posts: {len(user.posts)}")
                
        elif table.lower() == 'posts':
            posts = Post.query.all()
            click.echo(f"\n📝 Posts ({len(posts)}):")
            for post in posts:
                click.echo(f"   ID: {post.id} | {post.title[:50]}... | Author: {post.author.name}")
                
        elif table.lower() == 'contacts':
            contacts = Contact.query.all()
            click.echo(f"\n📞 Contacts ({len(contacts)}):")
            for contact in contacts:
                status = "✅ Read" if contact.is_read else "⭕ Unread"
                click.echo(f"   ID: {contact.id} | {contact.name} | {contact.email} | {status}")
        else:
            click.echo("❌ Available tables: users, posts, contacts")

if __name__ == '__main__':
    cli()