import "./styles.css";
import { LitElement, html } from "lit";
import { customElement, property } from "lit/decorators.js";

@customElement("messages-store-notification")
export class MessagesStoreNotification extends LitElement {
	@property({ type: String }) message = "";
	@property({ type: String }) type = "success";

	closeNotification() {
		this.dispatchEvent(new CustomEvent("close"));
	}

	createRenderRoot() {
		return this;
	}

	render() {
		return html`
			${this.message
				? html`
						<div
							class="fixed bottom-4 right-4 px-4 py-2 rounded shadow-lg z-50 ${this
								.type === "error"
								? "bg-red-500"
								: "bg-green-500"} text-white"
						>
							<div class="flex items-center">
								<span class="flex-grow">${this.message}</span>
								<button
									@click=${this.closeNotification}
									class="ml-4 text-white"
								>
									x
								</button>
							</div>
						</div>
					`
				: ""}
		`;
	}
}
