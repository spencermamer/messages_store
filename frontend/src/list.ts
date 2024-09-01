import "./styles.css";
import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("messages-store-list")
export class MessagesStoreList extends LitElement {
	@property({ type: Array }) messages = [];
	@property({ type: String }) sortOrder: "asc" | "desc" = "asc";
	@state() groupMessages = false; 

	createRenderRoot() {
		return this;
	}

	handleEdit(message) {
		this.dispatchEvent(new CustomEvent("edit", { detail: message }));
	}

	loadConfig() {
		const config = localStorage.getItem("messages-store-config");
		if (config) {
			this.groupMessages = JSON.parse(config).groupMessages;
		}
	}

	handleDelete(message) {
		this.loadConfig();
		const isEdit = message.originalMessage.length > 1;
		if (
			confirm(
				`Are you sure you want to delete the message with slug "${message.slug}"?`
			)
		) {
			if (isEdit && !this.groupMessages) {
				const newMessage = message.originalMessage.filter(
					(item) => item !== message.message
				);
				this.dispatchEvent(
					new CustomEvent("save", {
						detail: {
							slug: message.slug,
							messages: newMessage,
							service: "edit_message",
						},
					})
				);
			} else {
				this.dispatchEvent(
					new CustomEvent("delete", { detail: message.slug })
				);
			}
		}
	}

	formatMessage(message) {
		const style = "bg-zinc-700 p-0 px-0 font-semibold rounded shadow";
		return message
			.replace(
				/\(state:[^)]+\)/g,
				(match) => `<span class="${style}">${match}</span>`
			)
			.replace(
				/\(slug:[^)]+\)/g,
				(match) => `<span class="${style}">${match}</span>`
			)
			.replace(
				/%s/g,
				(match) => `<span class="${style}">${match}</span>`
			);
	}

	handleSortClick() {
		this.sortOrder = this.sortOrder === "asc" ? "desc" : "asc";
		this.dispatchEvent(new CustomEvent("sort", { detail: this.sortOrder }));
	}

	render() {
		return html`
			<table class="min-w-full text-sm border-collapse">
				<thead>
					<tr>
						<th
							class="px-4 py-3 text-left border-b border-zinc-600 w-1/5 cursor-pointer"
							@click=${this.handleSortClick}
						>
							Slug ${this.sortOrder === "asc" ? "↑" : "↓"}
						</th>
						<th
							class="px-4 py-3 text-left border-b border-zinc-600"
						>
							Message
						</th>
						<th
							class="px-4 py-3 text-left border-b border-zinc-600"
						></th>
					</tr>
				</thead>
				<tbody>
					${this.messages.map(
						(message: any, index) => html`
							<tr
								class="hover:bg-zinc-800"
								key="${message.slug + index}"
							>
								<td class="border-b border-zinc-600 px-4 py-3">
									<span
										class="bg-zinc-700 p-1 px-3 font-semibold rounded shadow"
									>
										${message.slug}
									</span>
								</td>
								<td class="border-b border-zinc-600 px-4 py-3">
									${message.message
										.split("| ")
										.map(
											(msg) => html`
												<div
													.innerHTML=${this.formatMessage(
														msg
													)}
												></div>
											`
										)}
								</td>
								<td
									class="border-b border-zinc-600 px-4 py-3 text-right"
								>
									<button
										class="text-zinc-300 hover:text-zinc-400 px-2 py-1"
										@click=${() => this.handleEdit(message)}
										title="Edit Message"
									>
										Edit
									</button>
									<button
										class="text-red-300 hover:text-red-400 ml-4 px-2 py-1"
										@click=${() =>
											this.handleDelete(message)}
										title="Delete Message"
									>
										Delete
									</button>
								</td>
							</tr>
						`
					)}
				</tbody>
			</table>
		`;
	}
}
