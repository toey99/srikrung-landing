# Chat Database Module for Sri Krung Chatbot
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

class ChatDatabase:
    def __init__(self, db_path: str = "chat_history.db"):
        """Initialize SQLite database for chat history"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if not exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                user_name TEXT,
                message TEXT NOT NULL,
                response TEXT,
                intent TEXT,
                handoff_requested BOOLEAN DEFAULT 0,
                handoff_reason TEXT,
                ai_handled BOOLEAN DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                session_id TEXT
            )
        ''')
        
        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_id TEXT PRIMARY KEY,
                display_name TEXT,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_active DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_messages INTEGER DEFAULT 0,
                handoff_count INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        # Notifications table for boss alerts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                type TEXT NOT NULL,
                message TEXT NOT NULL,
                is_read BOOLEAN DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_message(self, user_id: str, user_name: str, message: str, 
                     response: str = None, intent: str = None,
                     handoff_requested: bool = False, 
                     handoff_reason: str = None,
                     ai_handled: bool = True) -> int:
        """Save a chat message to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d')}"
        
        cursor.execute('''
            INSERT INTO chat_history 
            (user_id, user_name, message, response, intent, 
             handoff_requested, handoff_reason, ai_handled, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, user_name, message, response, intent,
              handoff_requested, handoff_reason, ai_handled, session_id))
        
        message_id = cursor.lastrowid
        
        # Update user session
        cursor.execute('''
            INSERT INTO user_sessions (user_id, display_name, last_active, total_messages)
            VALUES (?, ?, CURRENT_TIMESTAMP, 1)
            ON CONFLICT(user_id) DO UPDATE SET
                last_active = CURRENT_TIMESTAMP,
                total_messages = total_messages + 1
        ''', (user_id, user_name))
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_chat_history(self, user_id: str = None, limit: int = 50) -> List[Dict]:
        """Get chat history, optionally filtered by user_id"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if user_id:
            cursor.execute('''
                SELECT * FROM chat_history 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (user_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM chat_history 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_active_sessions(self) -> List[Dict]:
        """Get all active user sessions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM user_sessions 
            WHERE status = 'active'
            ORDER BY last_active DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def request_handoff(self, user_id: str, reason: str = "User requested"):
        """Mark user as needing human handoff"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE user_sessions 
            SET status = 'handoff', handoff_count = handoff_count + 1
            WHERE user_id = ?
        ''', (user_id,))
        
        conn.commit()
        conn.close()
    
    def create_notification(self, user_id: str, notif_type: str, message: str):
        """Create notification for boss"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO notifications (user_id, type, message)
            VALUES (?, ?, ?)
        ''', (user_id, notif_type, message))
        
        conn.commit()
        conn.close()
    
    def get_unread_notifications(self) -> List[Dict]:
        """Get all unread notifications"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM notifications 
            WHERE is_read = 0
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def mark_notification_read(self, notification_id: int):
        """Mark notification as read"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE notifications SET is_read = 1 WHERE id = ?
        ''', (notification_id,))
        
        conn.commit()
        conn.close()
    
    def get_stats(self) -> Dict:
        """Get chat statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total messages
        cursor.execute('SELECT COUNT(*) FROM chat_history')
        total_messages = cursor.fetchone()[0]
        
        # Total users
        cursor.execute('SELECT COUNT(*) FROM user_sessions')
        total_users = cursor.fetchone()[0]
        
        # Handoff requests
        cursor.execute('SELECT COUNT(*) FROM chat_history WHERE handoff_requested = 1')
        handoff_count = cursor.fetchone()[0]
        
        # Today's messages
        cursor.execute('''
            SELECT COUNT(*) FROM chat_history 
            WHERE date(timestamp) = date('now')
        ''')
        today_messages = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'total_users': total_users,
            'handoff_count': handoff_count,
            'today_messages': today_messages
        }

# Singleton instance
_db_instance = None

def get_db():
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ChatDatabase()
    return _db_instance