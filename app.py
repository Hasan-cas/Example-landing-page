@app.route('/request-paymemt', methods=['POST', 'GET'])
def request_payment():
    try:
        if request.method == 'POST':
            if 'csrf_token' not in request.form or request.form['csrf_token'] != session.get('csrf_token'):
                return render_template('request.html', text="Invaild request")
            existing_session = UserSession.query.filter_by(session_id=session.get('sid')).first()
            if existing_session :
                # Get form data
                user_id = session.get('user_id')
                viewer = Dashboard.query.filter_by(user_id=user_id).first()
                if not viewer :
                    return render_template("dashboard.html",text = "Try again later")
                amount = viewer.coin/10
                username = request.form['username']
                number = request.form['number']
                payment_provider = request.form['payment_provider']
                feedback= request.form['feedback']
                if not user_id or not amount or not username or not number or not payment_provider :
                    return render_template('request.html', text = " Some information is missing like user_id , username , number ,payment_provider etc")
                save_request = PaymentRequest(
                        user_id=user_id,# Creating a new user_id.
                        amount = amount,# amount of money
                        username = username, # persons name
                        number = number, # the phone number to send money
                        payment_provider = payment_provider, # bkeash or nogath
                        feedback = feedback, #user feedback

                        request_at = datetime.now(timezone.utc)
                        # Set expiry in 7 days
                        )
                db.session.add(save_request)
                db.session.commit()
                return render_template("request.html",text= "Thanks for your job . The Payment Request is send . You will recevie payment soon")
        elif request.method == 'GET':
            csrf_token = str(uuid4())
            # Generate a random CSRF token
            session['csrf_token'] = csrf_token

            return render_template('request.html', csrf_token = csrf_token )

    except Exception as e:
        # Capture details of the error
        ip_address = request.remote_addr  # Get IP address
        user_agent = request.user_agent.string  # Get user agent
        user_id = session.get('user_id', 'Not logged in')  # Get user ID from session

        # Log detailed error message
        logger.error(
            f"An error occurred:\n"
            f"  - Endpoint: {request.path}\n"
            f"  - Method: {request.method}\n"
            f"  - User ID: {user_id}\n"
            f"  - IP Address: {ip_address}\n"
            f"  - User Agent: {user_agent}\n"
            f"  - Error Message: {str(e)}"
        )

        # Render error template
        return render_template("error.html", message="An error occurred. Please try again.")

@app.route('/print-payment', methods=['GET'])
def print_payment():
    try:
        # Get form data
        payments = PaymentRequest.query.all()
        # Render the HTML for the table
        html_content = render_template('print.html', payments=payments)

        # Generate PDF from the HTML content
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        
        # Prepare the response with the PDF file
        pdf_file.seek(0)
        return Response(
            pdf_file,
            content_type='application/pdf',
            headers={
                'Content-Disposition': 'inline; filename="payment_table.pdf"'
            }
        )
    except Exception as e:
        # Capture details of the error
        ip_address = request.remote_addr  # Get IP address
        user_agent = request.user_agent.string  # Get user agent
        user_id = session.get('user_id', 'Not logged in')  # Get user ID from session

        # Log detailed error message
        logger.error(
            f"An error occurred:\n"
            f"  - Endpoint: {request.path}\n"
            f"  - Method: {request.method}\n"
            f"  - User ID: {user_id}\n"
            f"  - IP Address: {ip_address}\n"
            f"  - User Agent: {user_agent}\n"
            f"  - Error Message: {str(e)}"
        )
        # Render error template
        return render_template("error.html", message="An error occurred. Please try again.")
        