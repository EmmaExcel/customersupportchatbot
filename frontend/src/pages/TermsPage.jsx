import { Link } from 'react-router-dom'

export default function TermsPage() {
  return (
    <div className="page">
      <main className="legal-page">
        <p><Link to="/">Back to the demo</Link></p>
        <h1>Terms and Conditions</h1>
        <p className="legal-date">Last updated: September 18, 2026</p>

        <h2>Using the support chat</h2>
        <p>
          You may use this support chat to ask about products, view your
          account information, and place orders. You are responsible for the
          accuracy of the information you provide.
        </p>

        <h2>Placing orders</h2>
        <p>
          An order placed through the chat is only accepted when the system
          confirms it with an order number. Prices shown at the time of
          confirmation are the prices you pay. Stock availability can change
          before an order is confirmed.
        </p>

        <h2>Account access</h2>
        <p>
          Account actions in the chat use the account identifier associated
          with your support session. You must keep your login details private.
          Tell us right away if you believe someone else has used your account.
        </p>

        <h2>Acceptable use</h2>
        <p>
          You agree not to use the chat to attempt unauthorized access to
          systems or data, to interfere with the service, or to submit
          misleading order or account requests.
        </p>

        <h2>Service availability</h2>
        <p>
          We work to keep the support chat available, but we do not guarantee
          that it will be uninterrupted or error free. We may suspend access
          for maintenance or security reasons.
        </p>

        <h2>Liability</h2>
        <p>
          To the extent permitted by law, our total liability for claims
          arising from use of this chat is limited to the amount you paid for
          the order that gave rise to the claim.
        </p>

        <h2>Changes to these terms</h2>
        <p>
          We may update these terms. The updated version will be posted on this
          page with a new date.
        </p>

        <h2>Contact</h2>
        <p>
          Questions about these terms can be sent to legal@example.com.
        </p>
      </main>
    </div>
  )
}
