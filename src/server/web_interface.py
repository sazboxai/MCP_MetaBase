import os
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
from src.config.settings import Config
from src.api.metabase import MetabaseAPI

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, template_folder=Config.TEMPLATE_DIR)
    app.secret_key = os.urandom(24)
    
    @app.route('/')
    def home():
        """Home page with configuration form"""
        # Don't pass the actual API key to the template
        # Just indicate if one is set
        api_key_set = bool(Config._METABASE_API_KEY)
        
        return render_template(
            'config.html', 
            metabase_url=Config.METABASE_URL,
            api_key="" if not api_key_set else "••••••••••••••••••••••",
            api_key_set=api_key_set
        )
    
    @app.route('/save_config', methods=['POST'])
    def update_config():
        """Save configuration from form"""
        metabase_url = request.form.get('metabase_url', '').strip()
        api_key = request.form.get('api_key', '').strip()
        
        if not metabase_url:
            flash('Metabase URL is required!')
            return redirect(url_for('home'))
        
        # Only update API key if it's changed (not the masked version)
        if "•" not in api_key:
            Config.save_metabase_config(metabase_url, api_key)
            flash('Configuration saved successfully!')
        else:
            # Only update URL if API key wasn't changed
            with open(Config.CONFIG_FILE, 'w') as f:
                f.write(f"METABASE_URL={metabase_url}\n")
                f.write(f"METABASE_API_KEY={Config._METABASE_API_KEY}\n")
                f.write(f"SECRET_KEY={Config.SECRET_KEY}\n")
            
            # Update current environment and class attribute
            os.environ['METABASE_URL'] = metabase_url
            Config.METABASE_URL = metabase_url
            flash('URL updated successfully!')
        
        return redirect(url_for('home'))
    
    @app.route('/test_connection', methods=['POST'])
    async def test_connection():
        """Test connection with current or provided credentials"""
        metabase_url = request.form.get('metabase_url', Config.METABASE_URL).strip()
        api_key = request.form.get('api_key', '').strip()
        
        # Don't use the masked version
        if "•" in api_key:
            api_key = Config.get_metabase_api_key()
        
        # Temporarily update config for testing
        old_url = Config.METABASE_URL
        old_key = Config.get_metabase_api_key()
        Config.METABASE_URL = metabase_url
        
        try:
            success, message = await MetabaseAPI.test_connection()
            
            # Restore original config if not saving
            if 'save' not in request.form:
                Config.METABASE_URL = old_url
            
            return jsonify({'success': success, 'message': message})
        except Exception as e:
            # Restore original config
            Config.METABASE_URL = old_url
            
            # Return error as JSON
            return jsonify({'success': False, 'message': f"Error: {str(e)}"})
    
    @app.route('/test_list_databases')
    async def test_list_databases():
        """Test the list_databases tool"""
        from src.tools.metabase_tools import list_databases
        
        try:
            # Log the current configuration
            print(f"Testing list_databases with URL: {Config.get_metabase_url()}")
            
            result = await list_databases()
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            print(f"Error in test_list_databases: {str(e)}\n{error_traceback}")
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/test_get_metadata', methods=['POST'])
    async def test_get_metadata():
        """Test the get_database_metadata tool"""
        from src.tools.metabase_tools import get_database_metadata
        
        database_id = request.form.get('database_id')
        if not database_id or not database_id.isdigit():
            return jsonify({'success': False, 'error': 'Valid database ID is required'})
        
        try:
            result = await get_database_metadata(int(database_id))
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/test_list_actions')
    async def test_list_actions():
        """Test the list_actions tool"""
        from src.tools.metabase_action_tools import list_actions
        
        try:
            # Get version info
            version_info = await MetabaseAPI.get_request("version")
            version = "unknown"
            if version_info and not "error" in version_info:
                version = version_info.get("version", "unknown")
            
            result = await list_actions()
            result_with_version = f"Metabase Version: {version}\n\n{result}"
            
            return jsonify({'success': True, 'result': result_with_version})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/test_get_action_details', methods=['POST'])
    async def test_get_action_details():
        """Test the get_action_details tool"""
        from src.tools.metabase_action_tools import get_action_details
        
        action_id = request.form.get('action_id')
        if not action_id or not action_id.isdigit():
            return jsonify({'success': False, 'error': 'Valid action ID is required'})
        
        try:
            result = await get_action_details(int(action_id))
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/test_execute_action', methods=['POST'])
    async def test_execute_action():
        """Test the execute_action tool"""
        from src.tools.metabase_action_tools import execute_action
        
        action_id = request.form.get('action_id')
        if not action_id or not action_id.isdigit():
            return jsonify({'success': False, 'error': 'Valid action ID is required'})
        
        # Parse parameters from form
        parameters = {}
        for key, value in request.form.items():
            if key.startswith('param_'):
                param_name = key[6:]  # Remove 'param_' prefix
                parameters[param_name] = value
        
        try:
            result = await execute_action(int(action_id), parameters)
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/test_visualize_relationships', methods=['POST'])
    async def test_visualize_relationships():
        """Test the visualize_database_relationships tool"""
        from src.tools.metabase_tools import visualize_database_relationships
        
        database_id = request.form.get('database_id')
        if not database_id or not database_id.isdigit():
            return jsonify({'success': False, 'error': 'Valid database ID is required'})
        
        try:
            result = await visualize_database_relationships(int(database_id))
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    @app.route('/test_run_query', methods=['POST'])
    async def test_run_query():
        """Test the run_database_query tool"""
        from src.tools.metabase_tools import run_database_query
        
        database_id = request.form.get('database_id')
        query = request.form.get('query')
        
        if not database_id or not database_id.isdigit():
            return jsonify({'success': False, 'error': 'Valid database ID is required'})
        
        if not query or not query.strip():
            return jsonify({'success': False, 'error': 'SQL query is required'})
        
        try:
            result = await run_database_query(int(database_id), query)
            return jsonify({'success': True, 'result': result})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    return app

def run_web_interface():
    """Run the web interface"""
    app = create_app()
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.FLASK_DEBUG)

if __name__ == "__main__":
    run_web_interface() 