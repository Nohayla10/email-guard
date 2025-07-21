```markdown
# Security Notes for EmailGuard

This document outlines security considerations and best practices for deploying and using the EmailGuard project. While the core AI model focuses on classification, the application surrounding it must be secured to prevent misuse and protect data.

## 1. API Key Management

The Flask API (`backend/app.py`) uses an API key for authentication.

* **`API_KEY` Environment Variable:** The API key is loaded from the `API_KEY` environment variable (via a `.env` file locally).
    * **Recommendation:** **NEVER hardcode your API key** directly in `app.py` or commit it to version control.
    * **Best Practice:** In deployed environments (like Render, Railway, Vercel), use their built-in environment variable/secret management features to configure the `API_KEY` securely.
* **Strength:** Use a strong, long, and randomly generated API key. Avoid easily guessable keys.
* **Rotation:** Regularly rotate your API keys, especially if there's any suspicion of compromise.
* **Transmission:** Ensure the API key is always transmitted over **HTTPS/SSL/TLS** to prevent eavesdropping. Free hosting platforms typically provide HTTPS by default.

## 2. Input Validation

The `email_text` input to the `/scan` endpoint is critical.

* **Client-Side Validation:** While not strictly a security measure, client-side validation can improve UX and reduce unnecessary requests to the API.
* **Server-Side Validation:**
    * The `classify_email` method already checks for `non-empty string`.
    * **Recommendation:** Consider adding more robust validation if the `email_text` input could be excessively large, leading to denial-of-service (DoS) attacks or memory exhaustion. Set a maximum input size limit at the API gateway or application level.
    * **Encoding:** Ensure the input text is consistently handled with a known encoding (e.g., UTF-8) to prevent mojibake issues or parsing vulnerabilities.

## 3. Denial of Service (DoS) Prevention

* **Rate Limiting:** Implement rate limiting on your API endpoints (`/scan`, `/history`) to prevent a single client from overwhelming your service with requests. For Flask, libraries like `Flask-Limiter` can assist. Free-tier cloud providers might offer basic rate limiting, or you can implement it at the application layer.
* **Resource Limits:** The `TfidfVectorizer` and `LogisticRegression` model can consume memory and CPU, especially with very long texts or large vocabularies.
    * **Recommendation:** Consider setting limits on the input text length that the model will process. Implement timeouts for classification if it takes too long.
* **Containerization:** Deploying in containers (Docker) allows for easier resource allocation limits (CPU, RAM).

## 4. Logging and Monitoring

* **Error Logging:** The `backend/app.py` uses basic Python logging.
    * **Recommendation:** In production, configure a more robust logging system (e.g., to a centralized log management service or cloud-specific logging services).
    * Log unhandled exceptions, suspicious access attempts, and API errors.
* **Access Logs:** Monitor access logs for unusual patterns (e.g., too many requests from one IP, repeated failed authentication attempts).

## 5. Dependency Security

* **Vulnerability Scanning:** Regularly scan your project dependencies (`requirements.txt`) for known vulnerabilities using tools like `pip-audit`, `Snyk`, `Dependabot`, or `OWASP Dependency-Check`.
* **Keep Dependencies Updated:** Keep Flask, Werkzeug, scikit-learn, and other libraries updated to benefit from security patches.

## 6. Deployment Environment

* **HTTPS/TLS:** Always deploy the Flask API behind a production-grade web server (like Gunicorn, uWSGI) and an HTTPS proxy (like Nginx, Apache, or a load balancer) to ensure all traffic is encrypted. Free hosting platforms typically provide HTTPS automatically for deployed services.
* **Firewall Rules:** Restrict network access to your Flask application to only trusted sources or your load balancer/proxy.
* **Least Privilege:** Run the application with the minimum necessary user privileges.
* **Data Storage:** The current `SCAN_HISTORY` is in-memory and volatile. If persistent history is needed for a real application, store it in a secure database with appropriate access controls and encryption.

## 7. Model Security

* **Data Poisoning:** Be aware that if your model is ever retrained with external or user-provided data, it could be vulnerable to data poisoning attacks where malicious input aims to degrade model performance or induce specific misclassifications. For this project's scope (fixed pre-trained model), this risk is minimal.
* **Model Integrity:** Ensure the `email_guard_model.joblib` file is protected from unauthorized modification. Changes to this file could alter the model's behavior.

By following these guidelines, you can significantly enhance the security posture of your EmailGuard application.
