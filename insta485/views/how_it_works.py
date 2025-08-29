"""
Safe Transaction How it Works view.

URLs include:
/how-it-works/
"""
import flask
import insta485


@insta485.app.route('/how-it-works/')
def show_how_it_works():
    """Display the comprehensive How it Works page."""
    connection = insta485.model.get_db()
    
    # Get platform statistics for credibility
    stats_cur = connection.execute(
        """
        SELECT 
            COUNT(*) as total_transactions,
            COALESCE(SUM(CASE WHEN status = 'completed' THEN price ELSE 0 END), 0) as total_value,
            ROUND(
                CAST(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) AS FLOAT) / 
                NULLIF(COUNT(*), 0) * 100, 1
            ) as success_rate
        FROM transactions
        """
    )
    stats = stats_cur.fetchone()
    
    # Format stats for display  
    context = {
        'stats': {
            'total_transactions': f"{stats['total_transactions']:,}",
            'total_value': f"${stats['total_value']:,.0f}",
            'success_rate': f"{stats['success_rate']}%"
        }
    }
    
    return flask.render_template('how_it_works.html', **context)
