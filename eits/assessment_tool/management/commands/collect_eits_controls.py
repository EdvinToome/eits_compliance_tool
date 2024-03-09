import djclick as click
import requests

from ...models import Control


@click.command()
def command():
    response = requests.get("https://eits.ria.ee/api/2/article/2023")
    if response.status_code != 200:
        print(f"Failed to fetch data: {response.status_code}")
        return
    data = response.json()
    main_object = data[0] if data else {}

    def extract_data(obj):
        if isinstance(obj, dict):
            if 'title' in obj and obj.get('title') in ['3.2 Põhimeetmed', '3.3 Standardmeetmed',
                                                       '3.4 Kõrgmeetmed'] and 'id' in obj:
                for control in obj.get('child_objects', []):
                    Control.objects.get_or_create(
                        defaults={'control_id': control.get('id'), 'name': control.get('title')},
                        group_id=(control.get('title')).split(' ')[0], description=control.get('content'))
            for key, value in obj.items():
                if isinstance(value, (dict, list)):
                    extract_data(value)

        elif isinstance(obj, list):
            for item in obj:
                extract_data(item)

    extract_data(main_object)
