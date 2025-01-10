import requests
import psycopg2
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json

@csrf_exempt
def verify_recaptcha(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            recaptcha_response = data.get('recaptcha_response')

            # Get the client IP address
            if 'HTTP_X_FORWARDED_FOR' in request.META:
                user_ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
            else:
                user_ip = request.META.get('REMOTE_ADDR', '')

            if not recaptcha_response:
                return JsonResponse({'success': False, 'message': 'No se recibió ninguna respuesta reCAPTCHA.'})

            # Verify reCAPTCHA with Google's API
            response = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                data={
                    'secret': settings.RECAPTCHA_SECRET_KEY,
                    'response': recaptcha_response,
                    'remoteip': user_ip,  # Optional for additional validation
                },
            )
            result = response.json()

            if result.get('success'):
                # Connect to the external database and log the IP
                try:
                    conn = psycopg2.connect(
                        dbname=settings.EXTERNAL_DB_NAME,
                        user=settings.EXTERNAL_DB_USER,
                        password=settings.EXTERNAL_DB_PASSWORD,
                        host=settings.EXTERNAL_DB_HOST,
                        port=settings.EXTERNAL_DB_PORT,
                    )
                    cursor = conn.cursor()

                    # Ensure the IP is valid
                    if not user_ip:
                        return JsonResponse({'success': False, 'message': 'No se puede recuperar la dirección IP del usuario.'})

                    cursor.execute(
                        """
                        INSERT INTO ircaccess_alloweduser (ip_address)
                        VALUES (%s)
                        ON CONFLICT (ip_address) DO NOTHING;
                        """,
                        (user_ip,),
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()

                    return JsonResponse({'success': True, 'message': 'Verificación correcta! Ya puedes acceder al chat.'})
                except psycopg2.Error as db_error:
                    return JsonResponse({'success': False, 'message': f'Contacta con un OPerador en la sala #ayuda. Error de base de datos: {str(db_error)}'})

            else:
                error_codes = result.get('error-codes', [])
                return JsonResponse({'success': False, 'message': f'La verificación reCAPTCHA falló. Códigos de error: {error_codes}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Se produjo un error: {str(e)}'})

    return JsonResponse({'success': False, 'message': 'Método de solicitud no válido.'})

def home(request):
    return render(request, 'recaptcha_app/recaptcha_form.html', {'site_key': settings.RECAPTCHA_SITE_KEY})