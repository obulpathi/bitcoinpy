    def sendVersionMessage(self):
        #stuff version msg into sendbuf
        vt = msg_version()
        vt.addrTo.ip = self.dstaddr
        vt.addrTo.port = self.dstport
        vt.addrFrom.ip = "0.0.0.0"
        vt.addrFrom.port = 0
        vt.nStartingHeight = self.chaindb.getheight()
        vt.strSubVer = MY_SUBVERSION
        self.send_message(vt)

    def send_getblocks(self, timecheck=True):
        if not self.getblocks_ok:
            return
        now = time.time()
        if timecheck and (now - self.last_getblocks) < 5:
            return
        self.last_getblocks = now

        our_height = self.chaindb.getheight()
        if our_height < 0:
            gd = msg_getdata(self.ver_send)
            inv = CInv()
            inv.type = 2
            inv.hash = self.netmagic.block0
            gd.inv.append(inv)
            self.send_message(gd)
        elif our_height < self.remote_height:
            gb = msg_getblocks(self.ver_send)
            if our_height >= 0:
                gb.locator.vHave.append(self.chaindb.gettophash())
            self.send_message(gb)

