import "./styles.css";
import { LitElement, html } from "lit";
import { customElement, property, state } from "lit/decorators.js";

@customElement("notices-store-list")
export class NoticesStoreList extends LitElement {
	@property({ type: Array }) notices = [];
	@property({ type: String }) sortOrder: "asc" | "desc" = "asc";
	@state() groupNotices = true; // Renamed from groupMessages

	createRenderRoot() {
		return this;
	}

	handleEdit(notice) { // Renamed from message
		this.dispatchEvent(new CustomEvent("edit", { detail: notice }));
	}

	loadConfig() {
		const config = localStorage.getItem("notices-store-config"); // Renamed item
		if (config) {
			this.groupNotices = JSON.parse(config).groupNotices; // Renamed property
		}
	}

	handleDelete(notice) { // Renamed from message
		this.loadConfig();
		// Assuming originalMessage becomes originalNoticeContent or similar, passed in notice object
		const isEdit = notice.originalNoticeContent && notice.originalNoticeContent.length > 1;
		if (
			confirm(
				`Are you sure you want to delete the notice with slug "${notice.slug}"?` // Updated confirmation
			)
		) {
			if (isEdit && !this.groupNotices) {
				const newNoticeContent = notice.originalNoticeContent.filter(
					(item) => item !== notice.notice // Assuming notice.message becomes notice.notice
				);
				this.dispatchEvent(
					new CustomEvent("save", {
						detail: {
							slug: notice.slug,
							notice: newNoticeContent, // Renamed from messages to notice (singular, as per typical update)
							service: "edit_notice", // Updated service name
						},
					})
				);
			} else {
				this.dispatchEvent(
					new CustomEvent("delete", { detail: notice.slug })
				);
			}
		}
	}

	formatNotice(noticeContent) { // Renamed from formatMessage, parameter from message to noticeContent
		const style = "bg-zinc-700 p-0 px-0 font-semibold rounded shadow";
		return noticeContent // Renamed from message
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

	handleAcknowledgeToggle(notice) {
		this.dispatchEvent(new CustomEvent('acknowledge-toggle', {
			detail: {
				slug: notice.slug,
				acknowledged: !notice.acknowledged // Send the new desired state
			}
		}));
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
							Notice
						</th>
						<th
							class="px-4 py-3 text-left border-b border-zinc-600"
						></th>
					</tr>
				</thead>
				<tbody>
					${this.notices.map( // Renamed from this.messages
						(notice: any, index) => html` 
							<tr
								class="hover:bg-zinc-800"
								key="${notice.slug + index}"
							>
								<td class="border-b border-zinc-600 px-4 py-3">
									<span
										class="bg-zinc-700 p-1 px-3 font-semibold rounded shadow"
									>
										${notice.slug}
									</span>
								</td>
								<td class="border-b border-zinc-600 px-4 py-3">
									${notice.notice // Renamed from notice.message
										.split("| ")
										.map(
											(noticeContentPart) => html` 
												<div
													.innerHTML=${this.formatNotice( // Renamed from formatMessage
														noticeContentPart
													)}
												></div>
											`
										)}
									<div class="text-xs text-zinc-400 mt-1">
										<span>Priority: ${notice.priority !== undefined ? notice.priority : 'N/A'}</span> | 
										<span>Audience: ${notice.audience || 'N/A'}</span>
										${notice.expiration_date ? html` | <span>Expires: ${new Date(notice.expiration_date).toLocaleDateString()}</span>` : ''} | 
										<span>Acknowledged: ${notice.acknowledged ? 'Yes' : 'No'}</span>
									</div>
								</td>
								<td
									class="border-b border-zinc-600 px-4 py-3 text-right align-top"
								>
									<button
										class="text-zinc-300 hover:text-zinc-400 px-2 py-1"
										@click=${() => this.handleEdit(notice)}
										title="Edit Notice" 
									>
										Edit
									</button>
									<button
										class="text-red-300 hover:text-red-400 ml-4 px-2 py-1"
										@click=${() =>
											this.handleDelete(notice)}
										title="Delete Notice" 
									>
										Delete
									</button>
									<button
										class="text-blue-300 hover:text-blue-400 ml-4 px-2 py-1"
										@click=${() => this.handleAcknowledgeToggle(notice)}
										title=${notice.acknowledged ? "Mark as Unacknowledged" : "Mark as Acknowledged"}
									>
										${notice.acknowledged ? 'Unacknowledge' : 'Acknowledge'}
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
