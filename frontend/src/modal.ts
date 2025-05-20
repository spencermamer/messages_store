import "./styles.css";
import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("notices-store-modal") // Renamed component
export class NoticesStoreModal extends LitElement { // Renamed class
	@property({ type: Array }) allNotices: Array<any> = []; 
	@property({ type: String }) initialSlug = "";
	@property({ type: Array }) initialNoticeContents = []; 
	@property({ type: Number }) initialPriority;
	@property({ type: String }) initialAudience;
	@property({ type: String }) initialExpirationDate;
	// initialAcknowledged is passed but not edited in this step
	@property({ type: Object }) hass;

	@state() slug = "";
	@state() noticeContentList = [""]; 
	@state() priority: number = 3;
	@state() audience: string = 'all';
	@state() expirationDate: string = '';

	createRenderRoot() {
		return this;
	}

	connectedCallback() {
		super.connectedCallback();
		this.slug = this.initialSlug ?? "";
		this.noticeContentList = this.initialNoticeContents && this.initialNoticeContents.length > 0 ? [...this.initialNoticeContents] : [""];
		this.priority = this.initialPriority ?? 3;
		this.audience = this.initialAudience ?? 'all';
		this.expirationDate = this.initialExpirationDate ?? '';
		document.addEventListener("keydown", this.handleKeyDown);
	}

	disconnectedCallback() {
		document.removeEventListener("keydown", this.handleKeyDown);
		super.disconnectedCallback();
	}

	firstUpdated() {
		if (!this.initialSlug) {
			this.focusSlug();
		} else {
			this.focusNoticeContent(0); // Renamed from focusMessage
		}
	}

	handleKeyDown = (e: KeyboardEvent) => {
		if (e.key === "Escape") {
			this.closeModal();
		}
		if (e.ctrlKey && e.altKey && e.key.toLowerCase() === "s") {
			this.handleSave();
		}
	};

	handleAddNoticeContentItem() { // Renamed from handleAddMessage
		this.noticeContentList = [...this.noticeContentList, ""]; // Renamed from messageList
		setTimeout(() => this.focusNoticeContent(this.noticeContentList.length - 1), 0); // Renamed from focusMessage and messageList
	}

	handleRemoveNoticeContentItem(index: number) { // Renamed from handleRemoveMessage
		this.noticeContentList = this.noticeContentList.filter((_, i) => i !== index); // Renamed from messageList
	}

	handleSave() {
		const service = this.initialSlug ? "edit_notice" : "add_notice"; // Updated service names
		this.dispatchEvent(
			new CustomEvent("save", {
				detail: {
					slug: this.slug,
					notice: this.noticeContentList, 
					priority: this.priority,
					audience: this.audience,
					expiration_date: this.expirationDate || null, // Send null if empty
					service,
				},
			})
		);
	}

	closeModal() {
		this.dispatchEvent(new CustomEvent("close"));
	}

	focusSlug() {
		const slugInput: any =
			this.renderRoot.querySelector('input[type="text"]');
		if (slugInput) {
			slugInput.focus();
		}
	}

	focusNoticeContent(index: number) { // Renamed from focusMessage
		const noticeTextareas = this.renderRoot.querySelectorAll("textarea"); // Renamed from messageTextareas
		if (noticeTextareas && noticeTextareas[index]) { // Renamed from messageTextareas
			noticeTextareas[index].focus(); // Renamed from messageTextareas
		}
	}

	previewNoticeContent(noticeContent) { // Renamed from previewMessage, parameter from message to noticeContent
		return noticeContent // Renamed from message
			.replace(/\(slug:([^)]+)\)/g, (match, slugName) => {
				if (slugName === this.slug) {
					return match;
				}

				const matchingNotices: any = this.allNotices.filter( // Renamed from messages to allNotices
					(item) => item.slug === slugName // Renamed from msg to item
				);

				if (matchingNotices.length === 0) { // Renamed from matchingMessages
					return match;
				}

				const selectedNoticeContent = matchingNotices[0].notice; // Renamed from selectedMessage and matchingMessages[0].message

				if (/\(slug:[^)]+\)/.test(selectedNoticeContent)) { // Renamed from selectedMessage
					return match;
				}

				return selectedNoticeContent; // Renamed from selectedMessage
			})
			.replace(/\(state:([a-zA-Z0-9_\.]+)(?:\((.*?)\))?\)/g, (match, entityId, filters) => {
				const stateObj = this.hass.states[entityId];
				if (!stateObj) {
					return match;
				}
	
				let stateValue = stateObj.state;
				const unit = stateObj.attributes.unit_of_measurement || "";
				let finalValue = stateValue;

				const isNumeric = !isNaN(parseFloat(stateValue)) && isFinite(stateValue);
				filters = filters ? filters.split(',').map(f => f.trim()) : [];

				if (isNumeric) {
					stateValue = parseFloat(stateValue);

					if (filters.includes('round')) {
						finalValue = Math.round(stateValue);
					} else {
						const roundFilter = filters.find(f => f.startsWith('round'));
						if (roundFilter) {
							const decimals = parseInt(roundFilter.replace('round', ''), 10);
							finalValue = stateValue.toFixed(decimals);
						}
					}
				}

				if (filters.includes('unit') && unit) {
					finalValue = `${finalValue} ${unit}`;
				}

				return finalValue;
			});
	}

	render() {
		return html`
			<div
				class="fixed inset-0 flex items-center justify-center z-50 bg-zinc-900 bg-opacity-50 backdrop-blur-sm"
			>
				<div
					class="bg-zinc-800 text-white p-6 rounded-lg shadow-2xl w-full max-w-lg mx-4 sm:mx-6 md:w-2/3 lg:w-1/3 border-[1px] border-zinc-700"
				>
					<h2 class="text-xl mb-5 font-bold">
						${this.initialSlug ? "Edit Notice" : "Add Notice"} 
					</h2>
					<div class="mb-4">
						<label class="block mb-2 text-sm">Slug</label>
						<input
							type="text"
							class="text-sm outline-none border-b-2 border-zinc-600 bg-zinc-700 focus:border-zinc-400 focus:outline-none w-full p-2 text-white"
							.value=${this.slug}
							@input=${(e) => (this.slug = e.target.value)}
							?disabled=${!!this.initialSlug}
						/>
					</div>
					<div class="mb-4">
						<label class="block mb-2 text-sm">Notice Content</label> 
						${this.noticeContentList.map( 
							(noticeItem, index) => html` 
								<div class="flex flex-col mb-2">
									<div class="flex items-center">
										<textarea
											class="text-sm outline-none border-b-2 border-zinc-600 bg-zinc-700 focus:border-zinc-400 focus:outline-none w-full p-2 text-white mr-2"
											.value=${noticeItem} 
											@input=${(e) => {
												this.noticeContentList[index] = 
													e.target.value;
												this.requestUpdate();
											}}
										></textarea>
										${this.noticeContentList.length > 1 
											? html`
													<button
														class="bg-zinc-600 text-white px-3 py-1 font-bold rounded"
														@click=${() =>
															this.handleRemoveNoticeContentItem( 
																index
															)}
													>
														x
													</button>
												`
											: ""}
									</div>
									${/\(slug:[^)]+\)/.test(noticeItem) || 
									/\(state:[^)]+\)/.test(noticeItem) 
										? html`
												<div
													class="text-sm text-zinc-400 mt-2 mb-2"
												>
													<span class="text-zinc-300"
														>Preview:</span
													>
													${this.previewNoticeContent( 
														noticeItem 
													)}
												</div>
											`
										: ""}
								</div>
							`
						)}
						<button
							class="bg-zinc-500 text-white font-bold px-3 py-1 rounded mt-2"
							@click=${this.handleAddNoticeContentItem} 
						>
							+
						</button>
					</div>

					<div class="mb-4">
						<label class="block mb-2 text-sm">Priority (1-5)</label>
						<input
							type="number"
							min="1"
							max="5"
							class="text-sm outline-none border-b-2 border-zinc-600 bg-zinc-700 focus:border-zinc-400 focus:outline-none w-full p-2 text-white"
							.value=${this.priority.toString()}
							@input=${(e) => (this.priority = parseInt(e.target.value))}
						/>
					</div>

					<div class="mb-4">
						<label class="block mb-2 text-sm">Audience</label>
						<select
							class="text-sm outline-none border-b-2 border-zinc-600 bg-zinc-700 focus:border-zinc-400 focus:outline-none w-full p-2 text-white"
							.value=${this.audience}
							@change=${(e) => (this.audience = e.target.value)}
						>
							<option value="all">All</option>
							<option value="home">Home</option>
							<option value="not home">Not Home</option>
						</select>
					</div>

					<div class="mb-4">
						<label class="block mb-2 text-sm">Expiration Date (Optional, YYYY-MM-DD)</label>
						<input
							type="text"
							placeholder="YYYY-MM-DD"
							class="text-sm outline-none border-b-2 border-zinc-600 bg-zinc-700 focus:border-zinc-400 focus:outline-none w-full p-2 text-white"
							.value=${this.expirationDate}
							@input=${(e) => (this.expirationDate = e.target.value)}
						/>
					</div>
					
					<div class="flex justify-end">
						<button
							class="bg-green-500 text-white font-bold px-7 py-2 rounded mr-2"
							@click=${this.handleSave}
						>
							Save
						</button>
						<button
							class="bg-zinc-500 font-bold text-white px-7 py-2 rounded"
							@click=${this.closeModal}
						>
							Cancel
						</button>
					</div>
				</div>
			</div>
		`;
	}
}
