import * as path from 'path';
import { workspace, ExtensionContext } from 'vscode';

import {
    LanguageClient,
    LanguageClientOptions,
    ServerOptions,
    TransportKind
} from 'vscode-languageclient/node';

let client: LanguageClient;

export function activate(context: ExtensionContext) {
    // Get configuration
    const config = workspace.getConfiguration('trainingLanguageServer');
    const enabled = config.get<boolean>('enable', true);

    if (!enabled) {
        return;
    }

    const serverPath = config.get<string>('serverPath', 'training-lsp');

    // Server options: run the training-lsp command
    const serverOptions: ServerOptions = {
        command: serverPath,
        args: [],
        transport: TransportKind.stdio
    };

    // Client options: specify which documents to manage
    const clientOptions: LanguageClientOptions = {
        documentSelector: [
            { scheme: 'file', language: 'training' },
            { scheme: 'file', pattern: '**/*.training' },
            { scheme: 'file', pattern: '**/*.workout' },
            { scheme: 'file', pattern: '**/training*.txt' }
        ],
        synchronize: {
            fileEvents: workspace.createFileSystemWatcher('**/.{training,workout,txt}')
        }
    };

    // Create and start the language client
    client = new LanguageClient(
        'trainingLanguageServer',
        'Training Language Server',
        serverOptions,
        clientOptions
    );

    client.start();
}

export function deactivate(): Thenable<void> | undefined {
    if (!client) {
        return undefined;
    }
    return client.stop();
}
