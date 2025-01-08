@app.route('/request-paymemt', methods=['POST', 'GET'])
def request_payment():
    try:
        if request.method == 'POST':
            # CSRF token validation to prevent cross-site request forgery attacks
            if 'csrf_token' not in request.form or request.form['csrf_token'] != session.get('csrf_token'):
                return render_template('request.html', text="Invalid request")  # Respond with an error message if CSRF token is invalid

            # Fetch the existing session based on the session ID stored in the session
            existing_session = UserSession.query.filter_by(session_id=session.get('sid')).first()
            if existing_session:
                # If the session is valid, retrieve user data from the session
                user_id = session.get('user_id')
                viewer = Dashboard.query.filter_by(user_id=user_id).first()

                # Ensure the user exists in the dashboard
                if not viewer:
                    return render_template("dashboard.html", text="Try again later")  # Show an error if user data isn't found
                
                # Calculate the payment amount (based on user's coins)
                amount = viewer.coin / 10  # Amount is 1/10th of the user's coin value
                username = request.form['username']
                number = request.form['number']
                payment_provider = request.form['payment_provider']
                feedback = request.form['feedback']
                
                # Ensure all required form fields are provided
                if not user_id or not amount or not username or not number or not payment_provider:
                    return render_template('request.html', text="Some information is missing like user_id, username, number, payment_provider etc")

                # Save the payment request to the database
                save_request = PaymentRequest(
                    user_id=user_id,  # Creating a new user_id.
                    amount=amount,  # Amount of money
                    username=username,  # Person's name
                    number=number,  # Phone number for payment
                    payment_provider=payment_provider,  # Payment provider (bKash, Nogat)
                    feedback=feedback,  # User feedback
                    request_at=datetime.now(timezone.utc)  # Record the request time in UTC
                )

                # Add the payment request to the session and commit to the database
                db.session.add(save_request)
                db.session.commit()
                return render_template("request.html", text="Thanks for your job. The Payment Request is sent. You will receive payment soon.")
        
        elif request.method == 'GET':
            # Generate a new CSRF token for GET requests to prevent cross-site scripting
            csrf_token = str(uuid4())
            session['csrf_token'] = csrf_token

            return render_template('request.html', csrf_token=csrf_token)  # Send the CSRF token with the form

    except Exception as e:
        # Capture error details for logging and troubleshooting
        ip_address = request.remote_addr  # Get user's IP address
        user_agent = request.user_agent.string  # Get the user's browser and device details
        user_id = session.get('user_id', 'Not logged in')  # Get user ID or 'Not logged in' if the user is not authenticated

        # Log the error details with all relevant information
        logger.error(
            f"An error occurred:\n"
            f"  - Endpoint: {request.path}\n"
            f"  - Method: {request.method}\n"
            f"  - User ID: {user_id}\n"
            f"  - IP Address: {ip_address}\n"
            f"  - User Agent: {user_agent}\n"
            f"  - Error Message: {str(e)}"
        )

        # Render an error page if any exception occurs
        return render_template("error.html", message="An error occurred. Please try again.")

# Route for generating PDF of payment requests
@app.route('/print-payment', methods=['GET'])
def print_payment():
    try:
        # Fetch all payment requests from the database
        payments = PaymentRequest.query.all()

        # Render HTML for payment table
        html_content = render_template('print.html', payments=payments)

        # Generate PDF from HTML content
        pdf_file = BytesIO()
        HTML(string=html_content).write_pdf(pdf_file)
        
        # Prepare the response with the PDF file
        pdf_file.seek(0)
        return Response(
            pdf_file,
            content_type='application/pdf',
            headers={
                'Content-Disposition': 'inline; filename="payment_table.pdf"'  # Suggest downloading the PDF with a specified filename
            }
        )
    except Exception as e:
        # Capture error details for logging and troubleshooting
        ip_address = request.remote_addr  # Get user's IP address
        user_agent = request.user_agent.string  # Get the user's browser and device details
        user_id = session.get('user_id', 'Not logged in')  # Get user ID or 'Not logged in' if the user is not authenticated

        # Log the error details with all relevant information
        logger.error(
            f"An error occurred:\n"
            f"  - Endpoint: {request.path}\n"
            f"  - Method: {request.method}\n"
            f"  - User ID: {user_id}\n"
            f"  - IP Address: {ip_address}\n"
            f"  - User Agent: {user_agent}\n"
            f"  - Error Message: {str(e)}"
        )
        # Render an error page if any exception occurs
        return render_template("error.html", message="An error occurred. Please try again.")